import torch
from PIL import Image
from torchvision import transforms # type: ignore
import torchvision.models as models # type: ignore
import torch.nn as nn
import joblib
import numpy as np

# THIS CLASS CREATES A CUSTOM NEURAL NETWORK USING PRETRAINED RESNET50
class NutritionPredictor(nn.Module):
    def __init__(self, num_outputs=4):
        super().__init__()
        self.resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        # Remove classification layer (we are doing regression)
        self.feature_extractor = nn.Sequential(*list(self.resnet.children())[:-1])
        # Add dropout for regularization (during training)
        self.dropout = nn.Dropout(0.5)
        # Modified FC layer with more capacity
        self.fc = nn.Sequential(
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(1024, num_outputs)
        )
    def forward(self, x):
        x = self.feature_extractor(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        return self.fc(x)

# Load the model with the best weights
model = NutritionPredictor()
model.load_state_dict(torch.load("best_model.pth"))
model.eval()  

# Load the nutrition data scaler
scaler = joblib.load("nutrition_scaler.save")

# Define the image transformation (same as during training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),  
    transforms.ToTensor(),  
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def predict_nutrition(image_path):
    # Open the image
    image = Image.open(image_path).convert('RGB')
    # Apply transformations
    image = transform(image).unsqueeze(0) 
    # Make prediction
    with torch.no_grad():
        prediction = model(image)
    # Inverse transform the prediction to get actual nutrition values
    nutrition_values = scaler.inverse_transform(prediction.numpy())
    return {
        'Protein': nutrition_values[0][0],
        'Fat': nutrition_values[0][1],
        'Carbs': nutrition_values[0][2],
        'Total Calories': nutrition_values[0][3]
    }

# Example usage
if __name__ == "__main__":
    image_path = "testing.png"
    nutrition_info = predict_nutrition(image_path)
    print("Predicted Nutrition Information:")
    print(f"Protein: {nutrition_info['Protein']:.2f}g")
    print(f"Fat: {nutrition_info['Fat']:.2f}g")
    print(f"Carbs: {nutrition_info['Carbs']:.2f}g")
    print(f"Total Calories: {nutrition_info['Total Calories']:.2f}kcal")