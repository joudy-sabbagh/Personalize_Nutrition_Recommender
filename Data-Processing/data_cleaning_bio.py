import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load dataset
df = pd.read_csv("Dataset/original_bio.csv")

# Keep and rename relevant columns
df = df[[
    'subject',
    'Age',
    'Gender',
    'BMI',
    'Fasting GLU - PDL (Lab)',
    'Insulin ',
    'A1c PDL (Lab)'
]].rename(columns={
    'Body weight': 'weight_lb',
    'Height': 'height_in',
    'Fasting GLU - PDL (Lab)': 'fasting_glucose',
    'Insulin ': 'fasting_insulin',
    'A1c PDL (Lab)': 'HbA1c'
})

# Drop rows with missing values
df = df.dropna()

# Calculate HOMA-IR = (fasting_glucose * fasting_insulin) / 405
df['HOMA_IR'] = (df['fasting_glucose'] * df['fasting_insulin']) / 405

# Normalize numerical columns (excluding gender) -> we'll use an NN
numerical_cols = ['Age', 'fasting_glucose', 'fasting_insulin', 'BMI', 'HOMA_IR', 'HbA1c']
scaler = MinMaxScaler()
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# Convert gender to binary (0 = Female, 1 = Male)
df['Gender'] = df['Gender'].map({'F': 0, 'M': 1})

# Save final cleaned and normalized dataset
df.to_csv("Dataset/cleaned_clinical_data.csv", index=False)

print("Cleaned dataset saved as clinical_data.csv")