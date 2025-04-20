import pandas as pd

def calculate_binary_gut_health_rating():
    """
    Reads gut health scores per subject, removes nulls, computes average, 
    categorizes into binary health classes ('Good' or 'Bad'), and saves the results.
    """
    print("Reading gut health test data...")

    try:
        df = pd.read_csv("Dataset/original_gut_health_test.csv")
        print(f"Successfully loaded {len(df)} subjects")
    except Exception as e:
        print(f"Error loading the data: {e}")
        return

    # All columns except 'subject' are gut metrics
    gut_metrics = [col for col in df.columns if col != 'subject']

    # Drop rows with missing gut metric values
    initial_len = len(df)
    df = df.dropna(subset=gut_metrics)
    print(f"Removed {initial_len - len(df)} rows with missing values")

    # Compute average and round
    df['average_gut_score'] = df[gut_metrics].mean(axis=1).round(3)

    # Binary classification: Good vs Bad
    def categorize_binary(score):
        return 'Bad' if score < 1.6 else 'Good'

    df['gut_health_binary'] = df['average_gut_score'].apply(categorize_binary)

    # Save cleaned binary labels
    output_path = "Dataset/cleaned_gut_health.csv"
    df[['subject', 'average_gut_score', 'gut_health_binary']].to_csv(output_path, index=False)

    # Print summary
    print("\nSummary:")
    print(df['gut_health_binary'].value_counts())
    print("\nAverage scores stats:")
    print(f"Min: {df['average_gut_score'].min():.3f}")
    print(f"Max: {df['average_gut_score'].max():.3f}")
    print(f"Mean: {df['average_gut_score'].mean():.3f}")

    return df[['subject', 'average_gut_score', 'gut_health_binary']]

# Run it
if __name__ == "__main__":
    calculate_binary_gut_health_rating()
