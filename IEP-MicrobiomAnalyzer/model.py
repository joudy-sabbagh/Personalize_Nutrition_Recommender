import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


df = pd.read_csv('Data-Processing/Dataset/cleaned_microbes_and_gut.csv')

feature_cols = [c for c in df.columns if c not in ['subject', 'gut_health_category']]
X = df[feature_cols]
y = df['gut_health_category']

print("Original class distribution:")
print(y.value_counts())

le = LabelEncoder()
y_enc = le.fit_transform(y)

#unique_classes = le.classes_

X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, 
    test_size=0.20, 
    random_state=42
)

clf = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print("\nAccuracy: ", accuracy_score(y_test, y_pred))
#print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=unique_classes))

joblib.dump({
    'model': clf,
    'label_encoder': le,
    'features': feature_cols
}, 'gut_health_microbe_model.joblib')

print("\nModel, encoder, and feature list saved to 'gut_health_microbe_model.joblib'")

