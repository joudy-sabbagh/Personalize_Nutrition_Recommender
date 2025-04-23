import os
import pandas as pd
from datetime import datetime, timedelta
import requests

# === CONFIG ===
MAX_TOTAL_REQUESTS = 550
MIN_SPIKE_30 = 10  # Minimum spike at 30 min to consider the meal (mg/dL)
root_path = "Dataset/CGMacros"
output_path = "Dataset/GlucoseSpike_Data"
meal_gap = timedelta(minutes=15)
nutrition_api_url = "http://localhost:8000/analyze-meal"

os.makedirs(output_path, exist_ok=True)
total_requests = 0  # Global tracker

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
                nutrition_block.get("protein_pct"),
                nutrition_block.get("fat_pct"),
                nutrition_block.get("carbs_pct"),
                nutrition_block.get("sugar_risk"),
                nutrition_block.get("refined_carb")
            )
        else:
            print(f"Nutrition API failed for {img_name}: {response.status_code}")
    except Exception as e:
        print(f"Error for {img_name}: {e}")
    return (None, None, None, None, None, None)

# === MAIN LOOP ===
for user_folder in os.listdir(root_path):
    # Skip users before number 10
    try:
        user_num = int(user_folder.split("-")[-1])
        if user_num < 10:
            continue
    except:
        continue  # Skip folders that don't follow expected naming

    if total_requests >= MAX_TOTAL_REQUESTS:
        print(f"Reached global request limit of {MAX_TOTAL_REQUESTS}. Halting.")
        break

    user_path = os.path.join(root_path, user_folder)
    if not os.path.isdir(user_path):
        continue

    user_id = user_folder.split("-")[-1]
    csv_path = os.path.join(user_path, f"{user_folder}.csv")
    photos_path = os.path.join(user_path, "photos")

    if not os.path.exists(csv_path) or not os.path.exists(photos_path):
        continue

    df = pd.read_csv(csv_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values('Timestamp')

    # === Collect image timestamps ===
    photo_records = []
    for img_name in os.listdir(photos_path):
        if img_name.endswith(".jpg"):
            ts = extract_photo_timestamp(img_name)
            if ts:
                photo_records.append((img_name, ts))
    photo_records = sorted(photo_records, key=lambda x: x[1])

    # === Step 1: Get all spikes for all meals
    meal_records = []
    meal_id = 1
    prev_time = None

    for img_name, ts in photo_records:
        if prev_time is None or (ts - prev_time > meal_gap):
            meal_id += 1

        spike_30, spike_60 = get_glucose_spike(df, ts)

        if spike_30 is not None and spike_30 >= MIN_SPIKE_30:
            meal_records.append({
                "img_name": img_name,
                "timestamp": ts,
                "spike_30": spike_30,
                "spike_60": spike_60
            })

        prev_time = ts

    # === Step 2: Process all valid meals in order
    meal_records_sorted = sorted(meal_records, key=lambda x: x["timestamp"])
    records = []

    for meal in meal_records_sorted:
        if total_requests >= MAX_TOTAL_REQUESTS:
            print(f"Reached global request limit of {MAX_TOTAL_REQUESTS}. Halting.")
            break

        img_name = meal["img_name"]
        ts = meal["timestamp"]
        image_path = os.path.join(photos_path, img_name)

        caption, protein, fat, carbs, sugar_risk, refined_carb = get_nutrition_vector(image_path, img_name)

        if all(v is None for v in [protein, fat, carbs, sugar_risk, refined_carb]):
            print(f"Skipping {img_name} — no nutrition returned.")
            continue

        total_requests += 1

        records.append({
            "food_img": img_name,
            "timestamp": ts,
            "glucose_spike_30min": meal["spike_30"],
            "glucose_spike_60min": meal["spike_60"],
            "protein_pct": protein,
            "fat_pct": fat,
            "carbs_pct": carbs,
            "sugar_risk": sugar_risk,
            "refined_carb": refined_carb
        })

    final_df = pd.DataFrame(records)
    if "glucose_spike_30min" in final_df.columns and "glucose_spike_60min" in final_df.columns:
        final_df = final_df.dropna(subset=["glucose_spike_30min", "glucose_spike_60min"])
    else:
        print(f"Skipping {user_folder} — missing spike columns.")
        continue

    output_file = os.path.join(output_path, f"Glucose_Spike_User{user_id}.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Processed {user_folder} → {output_file}")
