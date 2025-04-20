import joblib
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import StandardScaler

def load_model_and_features(model_path):
    """Load model and associated feature information"""
    try:
        model_data = joblib.load(model_path)
        
        # Handle different save formats
        if isinstance(model_data, dict):
            return (
                model_data['model'],
                model_data['features'],
                model_data.get('scaler', StandardScaler())
            )
        else:
            # If model was saved directly without metadata
            # You'll need to provide features and scaler separately
            raise ValueError("Model missing feature metadata. Please provide features list.")
            
    except Exception as e:
        raise ValueError(f"Error loading model: {str(e)}")

def clean_column_names(df):
    """Clean and deduplicate column names consistently with training"""
    raw_cols = df.columns.astype(str)
    cleaned_cols = [re.sub(r'[\[\],<>]', '', col).strip() for col in raw_cols]
    
    counts = {}
    final_cols = []
    for col in cleaned_cols:
        counts[col] = counts.get(col, 0)
        final_cols.append(f"{col}_{counts[col]}" if counts[col] else col)
        counts[col] += 1
    
    df.columns = final_cols
    return df

def test_model(subject_id, model_path, data_path):
    """
    Test the trained model on a specific subject
    
    Args:
        subject_id (int): ID of the subject to test (46, 47, or 49)
        model_path (str): Path to the saved model file
        data_path (str): Path to the original microbiome data
    """
    try:
        # 1. Load model and feature information
        model, feature_cols, scaler = load_model_and_features(model_path)
        
        # 2. Load and preprocess data
        df = pd.read_csv(data_path)
        df = clean_column_names(df)
        
        # 3. Verify we have all required features
        missing_features = set(feature_cols) - set(df.columns)
        if missing_features:
            raise ValueError(f"Missing features in data: {missing_features}")
        
        # 4. Extract subject data
        subject_row = df[df['subject'] == subject_id]
        if subject_row.empty:
            raise ValueError(f"Subject {subject_id} not found")
            
        # 5. Prepare feature vector
        X = subject_row[feature_cols]
        X_scaled = scaler.transform(X) if hasattr(scaler, 'transform') else X.values
        
        # 6. Make prediction
        prob_good = model.predict_proba(X_scaled)[0, 1]
        prediction = "Good" if prob_good > 0.5 else "Bad"
        
        # 7. Format results
        print("\n" + "="*50)
        print(f"Subject {subject_id} Prediction Results:")
        print(f"- Probability of Good gut health: {prob_good:.3f}")
        print(f"- Predicted category: {prediction}")
        print("="*50 + "\n")
        
        return {
            'subject_id': subject_id,
            'probability_good': prob_good,
            'prediction': prediction
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Configuration
    MODEL_PATH = 'microbiome_model.pkl'
    DATA_PATH = '../Data-Processing/Dataset/cleaned_microbes_and_gut.csv'
    
    # Test the model
    test_model(49, MODEL_PATH, DATA_PATH)