import re
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc)
from sklearn.model_selection import StratifiedKFold, LeaveOneOut, cross_val_predict
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler

DATA_PATH = '../Data-Processing/Dataset/cleaned_microbes_and_gut.csv'
CV_FOLDS = 5
RANDOM_STATE = 42
MAX_FEATURES = 20  

def load_and_clean_data():
    """Load and clean column names to ensure consistency"""
    df = pd.read_csv(DATA_PATH)
    raw_cols = df.columns.astype(str).tolist()
    cleaned = [re.sub(r'[\[\],<>]', '', c).strip() for c in raw_cols]
    counts = {}
    final_cols = []
    for name in cleaned:
        counts[name] = counts.get(name, 0)
        final_cols.append(f"{name}_{counts[name]}" if counts[name] else name)
        counts[name] += 1
    df.columns = final_cols
    return df

def preprocess_data(df):
    """Handle missing values, feature selection, and scaling"""
    # Removes columns where variance is less than 0.01 (barely change across samples) -> not helpful for predictions
    selector = VarianceThreshold(threshold=0.01)
    X_sel = selector.fit_transform(df.drop(columns=['subject', 'gut_health_binary']))
    features = list(df.drop(columns=['subject', 'gut_health_binary']).columns[selector.get_support()])
    # Select top informative features using ANOVA F-test
    selector = SelectKBest(f_classif, k=min(MAX_FEATURES, len(features)))
    X_sel = selector.fit_transform(X_sel, (df['gut_health_binary'] == 'Good').astype(int))
    features = [features[i] for i in selector.get_support(indices=True)]
    # Scale features (turn to 0 and 1)
    scaler = StandardScaler()
    X_sel = scaler.fit_transform(X_sel)
    return X_sel, features, scaler  

def evaluate_model(model, X, y, cv_method, model_name=""):
    """Comprehensive model evaluation with multiple metrics"""
    print(f"\nEvaluating {model_name or model.__class__.__name__} with {cv_method.__class__.__name__}")
    # Get cross-validated predictions
    y_pred = cross_val_predict(model, X, y, cv=cv_method, method='predict_proba')[:,1]
    y_pred_class = (y_pred > 0.5).astype(int)
    # Calculate metrics
    acc = accuracy_score(y, y_pred_class)
    prec = precision_score(y, y_pred_class, zero_division=0)
    rec = recall_score(y, y_pred_class, zero_division=0)
    f1 = f1_score(y, y_pred_class, zero_division=0)
    fpr, tpr, _ = roc_curve(y, y_pred)
    roc_auc = auc(fpr, tpr)
    print(f"Accuracy: {acc:.3f}, Precision: {prec:.3f}, Recall: {rec:.3f}, F1: {f1:.3f}, AUC: {roc_auc:.3f}")
    # Plot ROC curve
    plt.figure()
    plt.plot(fpr, tpr, label=f'ROC (AUC={roc_auc:.2f})')
    plt.plot([0,1],[0,1],'--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {model_name or model.__class__.__name__}')
    plt.legend()
    plt.show()
    return model

def train_final_model(X, y, features, scaler):
    """Train an optimized ensemble model"""
    # Base model 1: xgboost
    xgb_model = XGBClassifier(
        objective='binary:logistic',
        max_depth=2,                            # Shallow tree -> prevent overfitting
        learning_rate=0.05,                     # Slows down learning so each tree contributes a small amount 
        n_estimators=100,                       # Build up to 100 tree
        reg_alpha=0.1,                          # L1 regularization -> adds a small penalty for using many features
        reg_lambda=1.0,                         # L2 regularization -> adds a stronger penalty for large weights (feature's importance)
        random_state=RANDOM_STATE
    )
    # Base Model 2: logistic regression
    lr_model = LogisticRegression(
        penalty='l2',                           # Add penalty for large weights
        C=0.1,                                  # Strong regularization, keep weights small and cautious
        solver='liblinear',                     # Algorithm that optimizes weights
        random_state=RANDOM_STATE
    )
    # Base Model 3: Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100,                      # Build up to 100 tree
        max_depth=3,                           # Shallow tree -> prevent overfitting
        random_state=RANDOM_STATE
    )
    # Create ensemble from 3 base model
    ensemble = VotingClassifier(
        estimators=[
            ('xgb', xgb_model),
            ('lr', lr_model),
            ('rf', rf_model)
        ],
        voting='soft'
    )
    # Train with SMOTE oversampling -> balance the data to have equal good and bad
    smote = SMOTE(random_state=RANDOM_STATE)
    X_res, y_res = smote.fit_resample(X, y)
    ensemble.fit(X_res, y_res)
    # Calibrate probabilities with StratifiedKFold (4 training, 1 validation) -> adjust model confidence level
    calibrated = CalibratedClassifierCV(
        ensemble,
        method='sigmoid',
        cv=StratifiedKFold(n_splits=min(5, np.bincount(y_res).min())))
    calibrated.fit(X_res, y_res)
    return calibrated

def save_model_with_metadata(model, features, scaler, filepath):
    """Save model with all necessary metadata"""
    model_data = {
        'model': model,
        'features': features,
        'scaler': scaler,
        'metadata': {
            'creation_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'num_features': len(features),
            'feature_names': features
        }
    }
    joblib.dump(model_data, filepath)
    print(f"Model saved to {filepath} with all metadata")

def main():
    # 1. Load and clean data
    df = load_and_clean_data()
    # 2. Preprocess data
    X, features, scaler = preprocess_data(df)  
    y = (df['gut_health_binary'] == 'Good').astype(int)
    print(f"\nClass Distribution: {np.bincount(y)} (Bad, Good)")
    print(f"Selected {len(features)} features:")
    print(features)
    # 3. Evaluate simple models first
    print("\n=== SIMPLE MODEL EVALUATION ===")
    lr = evaluate_model(
        LogisticRegression(penalty='l2', C=0.1, solver='liblinear'),
        X, y, LeaveOneOut(),
        model_name="Logistic Regression"
    )
    # Use smaller k-fold for RandomForest to ensure each class is represented
    min_class_count = np.bincount(y).min()
    n_splits = min(CV_FOLDS, min_class_count)
    rf = evaluate_model(
        RandomForestClassifier(n_estimators=100, max_depth=3),
        X, y, StratifiedKFold(n_splits=n_splits),
        model_name="Random Forest"
    )
    # 4. Train and evaluate final ensemble
    print("\n=== FINAL ENSEMBLE TRAINING ===")
    final_model = train_final_model(X, y, features, scaler)
    # 5. Final evaluation with StratifiedKFold
    print("\n=== FINAL MODEL EVALUATION ===")
    evaluate_model(
        final_model, 
        X, y, 
        StratifiedKFold(n_splits=n_splits),
        model_name="Final Ensemble"
    )
    # 6. Feature importance
    try:
        # Handle different model types for feature importance
        if hasattr(final_model.base_estimator, 'feature_importances_'):
            importances = final_model.base_estimator.feature_importances_
        elif hasattr(final_model, 'feature_importances_'):
            importances = final_model.feature_importances_
        elif hasattr(final_model, 'estimators_'):
            # For voting classifier, get average importance
            importances = np.mean([
                est.feature_importances_ 
                for est in final_model.estimators_ 
                if hasattr(est, 'feature_importances_')
            ], axis=0)
        else:
            raise AttributeError("No feature importance available")
        plt.figure(figsize=(10, 6))
        importance_df = pd.Series(importances, index=features).sort_values()
        importance_df.plot(kind='barh')
        plt.title('Feature Importance')
        plt.tight_layout()
        plt.show()
        print("\nTop 5 Most Important Features:")
        print(importance_df.nlargest(5))
    except Exception as e:
        print(f"Could not plot feature importance: {str(e)}")
    # 7. Save model with all necessary metadata
    save_model_with_metadata(final_model, features, scaler, 'microbiome_model.pkl')


if __name__ == "__main__":
    main()