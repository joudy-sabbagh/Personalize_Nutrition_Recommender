
from __future__ import annotations
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import joblib
import math

from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_regression
from sklearn.linear_model import ElasticNetCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import (KFold, cross_val_score, cross_val_predict,
                                     RandomizedSearchCV, train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor, VotingRegressor

# ------------------------ paths ------------------------------------------- #
PROJECT_ROOT = Path(__file__).parent.parent
CSV_FILE = PROJECT_ROOT / "Data-Processing" / "Dataset" / "filtered_merged_alldata.csv"
MODEL_DIR = Path(__file__).parent           # save models next to this script
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ------------------ config knobs ------------------------------------------ #
RANDOM_STATE = 42
KFOLDS       = 3      # Reduced from 5 to speed up training
TOP_K        = 100    # Reduced from 150 to improve stability
RAND_SEARCH  = 10     # Reduced from 30 to speed up training


# -------------------------------------------------------------------------- #
# 1)  load + light cleaning
# -------------------------------------------------------------------------- #
def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    
    print(f"Raw data shape: {df.shape}")
    print("Available columns:", df.columns.tolist()[:10], "...")
    
    # Check if target columns exist
    for target in ("glucose_spike_30min", "glucose_spike_60min"):
        if target not in df.columns:
            raise ValueError(f"Target column '{target}' not found in dataset. Available columns: {df.columns.tolist()}")

    # macro nutrients
    macro_map = {"low": 1, "medium": 2, "high": 3}
    for col in ["protein", "fat", "carbs"]:
        if col in df.columns:
            if df[col].dtype == 'object':  # Only convert if it's string
                df[col] = df[col].map(macro_map).astype(np.int8)
        else:
            print(f"Warning: Expected column '{col}' not found in data")

    # gut health flag (if present)
    if "microbe_gut_health_binary" in df.columns:
        if df["microbe_gut_health_binary"].dtype == 'object':  # Only convert if it's string
            df["microbe_gut_health_binary"] = (
                df["microbe_gut_health_binary"].str.lower().eq("good").astype(np.int8)
            )

    # timestamp features
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["weekday"] = df["timestamp"].dt.dayofweek
        
        # drop raw timestamp column after extracting features
        df = df.drop(columns=["timestamp"])

    # drop other raw text columns if they exist
    columns_to_drop = ["meal_id", "food_img", "caption"]
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    if existing_columns:
        df = df.drop(columns=existing_columns)

    # Ensure we only keep numeric columns
    df_numeric = df.select_dtypes(exclude="object")
    if df.shape[1] != df_numeric.shape[1]:
        dropped_cols = set(df.columns) - set(df_numeric.columns)
        print(f"Warning: Dropped non-numeric columns: {dropped_cols}")
    
    # Impute any remaining NaN values with mean
    for col in df_numeric.columns:
        if df_numeric[col].isna().any():
            df_numeric[col] = df_numeric[col].fillna(df_numeric[col].mean())
    
    return df_numeric


# -------------------------------------------------------------------------- #
# 2)  modelling helpers
# -------------------------------------------------------------------------- #
def make_pipeline(k_best: int | None = TOP_K) -> Pipeline:
    steps = []
    
    # Only include variance filter if we have many features
    steps.append(("var_filter", VarianceThreshold(threshold=0.005)))
    
    # Limit k to the number of features if needed
    steps.append(("select_k", SelectKBest(f_regression, k=k_best)))
    steps.append(("scale", StandardScaler(with_mean=False)))

    tree = HistGradientBoostingRegressor(random_state=RANDOM_STATE)

    # Increase max iterations to help convergence
    linear = ElasticNetCV(
        l1_ratio=[0.1, 0.5, 0.9],
        alphas=np.logspace(-3, 1, 10),  # Reduced number of alphas
        cv=KFOLDS,
        random_state=RANDOM_STATE,
        max_iter=2000,  # Increased from default 1000
        tol=1e-3,       # More lenient tolerance
        n_jobs=-1
    )

    ensemble = VotingRegressor(
        estimators=[("tree", tree)],  # Temporarily remove linear component
        weights=[1.0]
    )
    steps.append(("model", ensemble))
    return Pipeline(steps)


def tune_tree(X, y) -> dict:
    # Simplified parameter grid to speed up tuning
    param_dist = {
        "learning_rate": np.linspace(0.05, 0.2, 3),
        "max_depth": [None, 5],
        "l2_regularization": [0.1],
        "max_leaf_nodes": [31],
        "min_samples_leaf": [10],
    }
    
    try:
        search = RandomizedSearchCV(
            HistGradientBoostingRegressor(random_state=RANDOM_STATE),
            param_dist,
            n_iter=5,  # Further reduced
            cv=3,      # Fixed at 3
            scoring="r2",
            n_jobs=-1,
            random_state=RANDOM_STATE
        )
        search.fit(X, y)
        print(f"Best parameters: {search.best_params_}")
        return search.best_params_
    except Exception as e:
        print(f"Error in parameter tuning: {e}")
        # Return default parameters
        return {
            "learning_rate": 0.1,
            "max_depth": None,
            "l2_regularization": 0.1
        }


def cross_val_report(pipe: Pipeline, X, y, name: str):
    try:
        cv = KFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
        preds = cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

        r2  = r2_score(y, preds)
        mae = mean_absolute_error(y, preds)
        mse = mean_squared_error(y, preds)
        rmse = math.sqrt(mse)  # Calculate RMSE manually instead of using squared=False

        r2_std = cross_val_score(pipe, X, y, cv=cv, scoring="r2",
                              n_jobs=-1).std()

        print(f"\n{name} | CV R²={r2:.3f} (±{r2_std:.3f})  "
              f"MAE={mae:.3f}  RMSE={rmse:.3f}")
        return dict(R2=r2, MAE=mae, RMSE=rmse)
    except Exception as e:
        print(f"Error in cross-validation: {e}")
        return dict(R2=0, MAE=0, RMSE=0)


def persist_model(pipe: Pipeline, feature_names, target: str):
    try:
        out = MODEL_DIR / f"{target}_model.joblib"  # Simplified name
        joblib.dump(
            {
                "pipeline": pipe,
                "features": feature_names,
                "meta": {
                    "created": pd.Timestamp.now().isoformat(),
                    "top_k": TOP_K,
                    "kfolds": KFOLDS,
                    "model_ver": "v2-hgb"
                },
            },
            out
        )
        print(f"Saved → {out.name}")
    except Exception as e:
        print(f"Error saving model: {e}")


# -------------------------------------------------------------------------- #
# 3)  main
# -------------------------------------------------------------------------- #
def main():
    # Suppress all warnings
    warnings.filterwarnings("ignore")
    
    print(f"Looking for CSV file at: {CSV_FILE}")
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"Data file not found at {CSV_FILE}")

    df = load_data(CSV_FILE)
    print(f"Loaded dataset with shape {df.shape}")
    
    # Check if we have enough data
    if len(df) < 100:
        print("Warning: Dataset is very small, model performance may be poor")
    
    # Adjust TOP_K based on number of features
    actual_k = min(TOP_K, df.shape[1] - 3)  # Subtract targets and some buffer
    if actual_k < TOP_K:
        print(f"Warning: Reduced feature selection to {actual_k} (fewer columns than TOP_K={TOP_K})")

    for target in ("glucose_spike_30min", "glucose_spike_60min"):
        print("\n" + "=" * 70)
        print(f"Training target: {target}")
        
        try:
            # Split data into 80% training and 20% testing BEFORE any processing
            train_df, test_df = train_test_split(df, test_size=0.20, random_state=RANDOM_STATE)
            print(f"Training data size: {len(train_df)} samples (80%)")
            print(f"Testing data size: {len(test_df)} samples (20%)")
            
            # Training data preparation
            X_train = train_df.drop(columns=[target])
            y_train = train_df[target].values
            
            # Testing data preparation
            X_test = test_df.drop(columns=[target])
            y_test = test_df[target].values
            
            print(f"Training with {X_train.shape[1]} features")

            pipe = make_pipeline(k_best=actual_k)

            # Hyperparameter tuning on training data only
            # (using a subset of training data for validation)
            X_train_subset, X_val, y_train_subset, y_val = train_test_split(
                X_train, y_train, test_size=0.20, random_state=RANDOM_STATE
            )
            
            # Get best parameters for tree using subset of training data
            best_params = tune_tree(X_train_subset, y_train_subset)
            
            # Update tree in the ensemble
            try:
                pipe.named_steps["model"].estimators[0][1].set_params(**best_params)
            except Exception as e:
                print(f"Error updating tree parameters: {e}")
                # Try a direct replacement if the update fails
                tree = HistGradientBoostingRegressor(random_state=RANDOM_STATE, **best_params)
                pipe.named_steps["model"].estimators[0] = ("tree", tree)

            # Fit the model on the training data only
            print("Fitting model on training data...")
            pipe.fit(X_train, y_train)
            
            # Evaluate on the test set
            y_pred = pipe.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = math.sqrt(mse)
            
            print(f"\nTest Set Evaluation for {target}:")
            print(f"R² Score: {r2:.3f}")
            print(f"Mean Absolute Error: {mae:.3f}")
            print(f"Root Mean Squared Error: {rmse:.3f}")
            
            # Save model
            persist_model(pipe, X_train.columns.tolist(), target)
            
        except Exception as e:
            print(f"Error processing {target}: {e}")

    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error in main execution: {e}")
