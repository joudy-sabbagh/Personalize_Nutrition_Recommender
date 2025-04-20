import pandas as pd

def calculate_gut_health_rating_from_test():
    """
    Reads gut health scores per subject, removes nulls, computes average, 
    categorizes into health classes, and saves the results.
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

    # Drop rows with any nulls in gut metric columns
    initial_len = len(df)
    df = df.dropna(subset=gut_metrics)
    print(f"Removed {initial_len - len(df)} rows with missing values")

    # Calculate average score across all metrics and round to 3 decimals
    df['average_gut_score'] = df[gut_metrics].mean(axis=1).round(3)

    # Categorize each subject
    def categorize(score):
        if score < 1.6:
            return 'Not Healthy'
        elif score < 2.3:
            return 'Okay'
        else:
            return 'Healthy'

    df['gut_health_category'] = df['average_gut_score'].apply(categorize)

    # Save the new cleaned file
    output_path = "Dataset/cleaned_gut_health.csv"
    df[['subject', 'average_gut_score', 'gut_health_category']].to_csv(output_path, index=False)

    # Print summary
    print("\nSummary:")
    print(df['gut_health_category'].value_counts())
    print("\nAverage scores stats:")
    print(f"Min: {df['average_gut_score'].min():.3f}")
    print(f"Max: {df['average_gut_score'].max():.3f}")
    print(f"Mean: {df['average_gut_score'].mean():.3f}")

    return df[['subject', 'average_gut_score', 'gut_health_category']]

# Run it
if __name__ == "__main__":
    calculate_gut_health_rating_from_test()