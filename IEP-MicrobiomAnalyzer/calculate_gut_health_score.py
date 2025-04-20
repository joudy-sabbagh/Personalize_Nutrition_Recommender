import pandas as pd
import numpy as np

def calculate_gut_health_rating():
    """
    This function reads the gut health data, calculates the average score across 
    22 gut metrics, categorizes each subject, and saves the results to a new CSV file.
    
    Categories:
    - 1.0–1.6 → 'Not Healthy'
    - 1.6–2.3 → 'Okay'
    - 2.3–3.0 → 'Healthy'
    """
    print("Reading gut health data...")
    
    # Read the gut health data
    try:
        df = pd.read_csv("Data-Processing/cleaned_gut_health_data.csv")
        print(f"Successfully loaded data with {len(df)} subjects")
    except Exception as e:
        print(f"Error loading the data: {e}")
        return
    
    # Define the 22 gut health metrics (all columns after PC35)
    gut_metrics = [
        'Gut Lining Health', 'LPS Biosynthesis Pathways', 
        'Biofilm, Chemotaxis, and Virulence Pathways', 'TMA Production Pathways',
        'Ammonia Production Pathways', 'Metabolic Fitness', 'Active Microbial Diversity',
        'Butyrate Production Pathways', 'Flagellar Assembly Pathways',
        'Putrescine Production Pathways', 'Uric Acid Production Pathways',
        'Bile Acid Metabolism Pathways', 'Inflammatory Activity',
        'Gut Microbiome Health', 'Digestive Efficiency', 'Protein Fermentation',
        'Gas Production', 'Methane Gas Production Pathways',
        'Sulfide Gas Production Pathways', 'Oxalate Metabolism Pathways',
        'Salt Stress Pathways', 'Microbiome-Induced Stress'
    ]
    
    # Verify the columns exist in the dataframe
    missing_columns = [col for col in gut_metrics if col not in df.columns]
    if missing_columns:
        print(f"Warning: The following columns are missing: {missing_columns}")
        # Filter out missing columns
        gut_metrics = [col for col in gut_metrics if col in df.columns]
        print(f"Proceeding with available columns: {gut_metrics}")
    
    # Create a new dataframe with just subject ID and the gut health metrics
    result_df = pd.DataFrame({'subject': df['subject']})
    
    # Filter out rows with missing values in gut metrics
    valid_rows = df[gut_metrics].notna().all(axis=1)
    if not valid_rows.all():
        print(f"Warning: {(~valid_rows).sum()} rows have missing values and will be excluded")
        df = df[valid_rows].copy()
        result_df = pd.DataFrame({'subject': df['subject']})
    
    # Calculate the mean score across all metrics for each subject
    result_df['average_gut_score'] = df[gut_metrics].mean(axis=1)
    
    # Categorize based on the average score
    def categorize_score(score):
        if score < 1.6:
            return 'Not Healthy'
        elif score < 2.3:
            return 'Okay'
        else:
            return 'Healthy'
    
    result_df['gut_health_category'] = result_df['average_gut_score'].apply(categorize_score)
    
    # Round the average score to 2 decimal places
    result_df['average_gut_score'] = result_df['average_gut_score'].round(2)
    
    # Save to a new CSV file
    output_path = "Data-Processing/gut_health_target.csv"
    result_df.to_csv(output_path, index=False)
    
    print(f"Results saved to {output_path}")
    
    # Print a summary
    category_counts = result_df['gut_health_category'].value_counts()
    print("\nSummary:")
    for category, count in category_counts.items():
        print(f"{category}: {count} subjects")
    
    print("\nAverage scores distribution:")
    print(f"Min: {result_df['average_gut_score'].min()}")
    print(f"Max: {result_df['average_gut_score'].max()}")
    print(f"Mean: {result_df['average_gut_score'].mean():.2f}")
    
    return result_df

if __name__ == "__main__":
    calculate_gut_health_rating() 