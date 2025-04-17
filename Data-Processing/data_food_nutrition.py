import json
import pandas as pd

# THIS FUNCTION CALCULATES TOTAL AMOUNT OF CARBS
def calculate_carbs(nrg, fat, protein):
    calories_from_fat = fat * 9
    calories_from_protein = protein * 4
    calories_from_carbs = nrg - (calories_from_fat + calories_from_protein)
    carbs = calories_from_carbs / 4  # 1g of carbs = 4 kcal
    return carbs

# Load the JSON files
with open('../../recipes_with_nutritional_info.json') as f:
    recipes_data = json.load(f)

with open('../../layer2+.json', encoding='utf-8-sig') as f:
    image_data = json.load(f)

# Step 1: Create a mapping of recipe id to image id
image_mapping = {}
for item in image_data:
    recipe_id = item['id']  # outer 'id' is the recipe ID
    for image in item['images']:
        image_mapping[recipe_id] = image['id']  # mapping recipe_id to image_id

# Step 2: Loop through each recipe and link image id
nutritional_info = []

for recipe in recipes_data:
    recipe_id = recipe['id']
    
    # Initialize variables for nutritional data
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    
    # Extract nutritional values from 'nutr_values_per100g'
    nutrition = recipe.get('nutr_values_per100g', {})
    
    total_protein = nutrition.get('protein', 0)        
    total_fat = nutrition.get('fat', 0)
    total_calories = nutrition.get('energy', 0)
    total_carbs = calculate_carbs(total_calories, total_fat, total_protein)
    
    # Link recipe id to image id
    image_id = image_mapping.get(recipe_id, None)

    # Extract the title
    recipe_title = recipe.get('title', 'No title')  # default to 'No title' if missing
    
    # Append the results to the list
    nutritional_info.append({
        'id': recipe_id,
        'title': recipe_title,  # Add the title
        'protein': total_protein,
        'fat': total_fat,
        'carbs': total_carbs,
        'total_calories': total_calories,
        'image_id': image_id
    })

    print(f"Finished recipe {recipe_id}")

# Optionally: Save to CSV
df = pd.DataFrame(nutritional_info)
df.to_csv('Dataset/nutrition_info.csv', index=False)
