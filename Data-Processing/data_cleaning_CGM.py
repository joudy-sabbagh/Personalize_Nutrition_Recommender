import os
import pandas as pd
from datetime import datetime, timedelta
import requests

# === CONFIG ===
root_path = "Dataset/CGMacros"
output_path = "Dataset/GlucoseSpike_Data"
meal_gap = timedelta(minutes=15)
nutrition_api_url = "http://localhost:8000/analyze-meal"

# Create output folder if it doesn't exist
os.makedirs(output_path, exist_ok=True)

# === FUNCTIONS ===

def extract_photo_timestamp(name):
    try:
        parts = name.replace('.jpg', '').split('-')
        for i in range(len(parts) - 5):
            try:
                year, month, day, hour, minute, _ = map(int, parts[i:i+6])
                return datetime(year, month, day, hour, minute)
            except:
                continue
        raise ValueError("No valid timestamp format found.")
    except Exception as e:
        print(f"Skipping timestamp extraction for {name}: {e}")
        return None

def get_glucose_spike(df, meal_time):
    def closest_value(t):
        return df.iloc[(df['Timestamp'] - t).abs().argsort()[:1]]
    try:
        t0 = closest_value(meal_time)['Dexcom GL'].values[0]
        t30 = closest_value(meal_time + timedelta(minutes=30))['Dexcom GL'].values[0]
        t60 = closest_value(meal_time + timedelta(minutes=60))['Dexcom GL'].values[0]
        return t30 - t0, t60 - t0
    except:
        return None, None

def get_nutrition_vector(image_path, img_name):
    try:
        with open(image_path, "rb") as image_file:
            response = requests.post(
                nutrition_api_url,
                files={"image": (img_name, image_file, "image/jpeg")}
            )
        if response.status_code == 200:
            data = response.json()
            caption = data.get("caption")
            nutrition_block = data.get("nutrition", {}).get("nutrition", {})

            return (
                caption,
                nutrition_block.get("protein"),
                nutrition_block.get("fat"),
                nutrition_block.get("carbs")
            )
        else:
            print(f"Nutrition API failed for {img_name}: {response.status_code}")
    except Exception as e:
        print(f"Error for {img_name}: {e}")
    return (None, None, None, None)

# === MAIN LOOP ===
for user_folder in os.listdir(root_path):
    user_path = os.path.join(root_path, user_folder)
    if not os.path.isdir(user_path):
        continue

    user_id = user_folder.split("-")[-1]
    csv_path = os.path.join(user_path, f"{user_folder}.csv")
    photos_path = os.path.join(user_path, "photos")

    if not os.path.exists(csv_path) or not os.path.exists(photos_path):
        continue

    # Load glucose data
    df = pd.read_csv(csv_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values('Timestamp')

    # Collect photo timestamps
    photo_records = []
    for img_name in os.listdir(photos_path):
        if img_name.endswith(".jpg"):
            ts = extract_photo_timestamp(img_name)
            if ts:
                photo_records.append((img_name, ts))
    photo_records = sorted(photo_records, key=lambda x: x[1])

    # Assign meal IDs and calculate spikes + nutrition
    records = []
    meal_id = 1
    prev_time = None

    for img_name, ts in photo_records:
        if prev_time is None or (ts - prev_time > meal_gap):
            meal_id += 1
        spike_30, spike_60 = get_glucose_spike(df, ts)

        image_path = os.path.join(photos_path, img_name)
        caption, protein, fat, carbs = get_nutrition_vector(image_path, img_name)

        records.append({
            "meal_id": meal_id,
            "food_img": img_name,
            "timestamp": ts,
            "glucose_spike_30min": spike_30,
            "glucose_spike_60min": spike_60,
            "caption": caption,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        })

        prev_time = ts

    final_df = pd.DataFrame(records)
    final_df = final_df.dropna(subset=["glucose_spike_30min", "glucose_spike_60min"])

    # Save to user-specific CSV
    output_file = os.path.join(output_path, f"Glucose_Spike_User{user_id}.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Processed {user_folder} → {output_file}")