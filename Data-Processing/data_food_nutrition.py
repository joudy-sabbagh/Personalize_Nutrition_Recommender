import json
import pandas as pd

# THIS FUNCTION CALCULATES TOTAL AMOUNT OF CARBS
def calculate_carbs(nrg, fat, protein):
    calories_from_fat = fat * 9
    calories_from_protein = protein * 4
    calories_from_carbs = nrg - (calories_from_fat + calories_from_protein)
    carbs = calories_from_carbs / 4  # 1g of carbs = 4 kcal
    return carbs

# Load the JSON file
with open('../../recipes_with_nutritional_info.json') as f:
    data = json.load(f)

# Create a list to store the extracted nutritional info
nutritional_info = []

# Loop through each recipe
for recipe in data:  
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

    # Append the results to the list
    nutritional_info.append({
        'id': recipe_id,
        'protein': total_protein,
        'fat': total_fat,
        'carbs': total_carbs,
        'total_calories': total_calories
    })

    print("Finished recipe " + recipe_id)

# Optionally: Save to CSV
df = pd.DataFrame(nutritional_info)
df.to_csv('nutrition_info.csv', index=False)