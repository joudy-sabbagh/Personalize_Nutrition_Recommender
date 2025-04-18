import ast
import re
from collections import Counter
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import pipeline

# 1) Load the NER pipeline (only once)
ner = pipeline(
    "token-classification",
    model="edwardjross/xlm-roberta-base-finetuned-recipe-all",
    aggregation_strategy="simple"
)

# 2) Load & clean your CSV
df = pd.read_csv('Dataset/Food_Information.csv')
df = df.drop(columns=['Unnamed: 0']).dropna(subset=['Cleaned_Ingredients','Image_Name'])
print("Null counts after drop:\n", df[['Cleaned_Ingredients','Image_Name']].isnull().sum())

# 3) Extract ingredient names via the NER model
def extract_names(list_str):
    """
    - literal_eval the list‑literal string
    - run each entry through the NER pipeline
    - collect all NAME spans and dedupe
    """
    try:
        raw = ast.literal_eval(list_str)
    except (ValueError, SyntaxError):
        return []

    seen, out = set(), []
    for phrase in raw:
        ents = ner(phrase)
        for e in ents:
            if e["entity_group"] == "NAME":
                name = e["word"].strip().lower()
                if name and name not in seen:
                    seen.add(name)
                    out.append(name)
    return out

# To have a baseline model ~7k is good
df_sampled = df.sample(n=7000, random_state=42).reset_index(drop=True)
df_sampled['ingredient_list'] = df_sampled['Cleaned_Ingredients'].apply(extract_names)

# 4) Quick sanity check
print(df_sampled['ingredient_list'].head(5))

# 5) Build vocab & index mapping
df_sampled['ingredient_list'] = df_sampled['ingredient_list'].apply(
    lambda x: x if isinstance(x, list) else []
)

# now this will never see a float
all_ings = [ing for sub in df_sampled['ingredient_list'] for ing in sub]
counts  = Counter(all_ings)
vocab   = sorted(counts)
ing2idx = {ing: i for i,ing in enumerate(vocab)}

# 6) Multi‑hot encoding
def encode_multi_hot(ings):
    vec = np.zeros(len(vocab), dtype=int)
    for ing in ings:
        idx = ing2idx.get(ing)
        if idx is not None:
            vec[idx] = 1
    return vec

df_sampled['multi_hot'] = df_sampled['ingredient_list'].apply(encode_multi_hot)

# 7) Train/Val/Test split (80/10/10)
train_df, temp_df = train_test_split(df_sampled, test_size=0.20, random_state=42)
val_df,  test_df  = train_test_split(temp_df, test_size=0.50, random_state=42)

# Save processed dataframes to CSV files
train_df.to_csv('Dataset/train_food_info.csv', index=False)
val_df.to_csv('Dataset/val_food_info.csv', index=False)
test_df.to_csv('Dataset/test_food_info.csv', index=False)

print("Dataframes successfully saved.")

# 8) Summary
print(f"Total records: {len(df_sampled)}")
print(f"Train: {len(train_df)}, Valid: {len(val_df)}, Test: {len(test_df)}")
print(f"Vocabulary size: {len(vocab)}")
print("Sample vocab items:", vocab[:20])
