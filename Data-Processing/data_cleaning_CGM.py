import os
import pandas as pd
from datetime import datetime, timedelta

# === CONFIG ===
root_path = "Dataset/CGMacros"
output_path = "Dataset/GlucoseSpike_Data"
meal_gap = timedelta(minutes=15)

# Create output folder if it doesn't exist
os.makedirs(output_path, exist_ok=True)

# === FUNCTIONS ===

def extract_photo_timestamp(name):
    parts = name.split('-PHOTO-')[-1].replace('.jpg', '').split('-')
    return datetime(
        year=int(parts[0]),
        month=int(parts[1]),
        day=int(parts[2]),
        hour=int(parts[3]),
        minute=int(parts[4])
    )

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
            photo_records.append((img_name, ts))
    photo_records = sorted(photo_records, key=lambda x: x[1])

    # Assign meal IDs and calculate spikes
    records = []
    meal_id = 1
    prev_time = None

    for img_name, ts in photo_records:
        if prev_time is None or (ts - prev_time > meal_gap):
            meal_id += 1
        spike_30, spike_60 = get_glucose_spike(df, ts)

        records.append({
            "meal_id": meal_id,
            "food_img": img_name,
            "timestamp": ts,
            "glucose_spike_30min": spike_30,
            "glucose_spike_60min": spike_60
        })

        prev_time = ts

    final_df = pd.DataFrame(records)
    final_df = final_df.dropna(subset=["glucose_spike_30min", "glucose_spike_60min"])

    # Save to user-specific CSV
    output_file = os.path.join(output_path, f"Glucose_Spike_User{user_id}.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Processed {user_folder} → {output_file}")
