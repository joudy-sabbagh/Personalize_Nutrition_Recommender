import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms # type: ignore
import torch
import torch.nn as nn
import torchvision.models as models # type: ignore
from torch.optim import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib  

# Load dataset
df = pd.read_csv("../Data-Processing/Dataset/Food_Information_With_Nutrition.csv")
# Define image path
image_folder = "../../Food Images/Food Images"  

# Normalize nutrition data for the model to learn
scaler = StandardScaler()
nutrition_data = scaler.fit_transform(df[['Protein', 'Fat', 'Carbs', 'Total Calories']])
joblib.dump(scaler, 'nutrition_scaler.save')  # Save the scaler for later use

# Preparing Image Paths and Nutrition Data
image_paths = df['Image_Name'].apply(lambda x: f"{image_folder}/{x}.jpg").tolist()

# Pre-Process images
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


# THIS CLASS TELLS THE MODEL HOW TO LOAD IMAGE AND MATCH THEM TO CORRECT NUTRITION VALUE
class FoodDataset(Dataset):
    def __init__(self, image_paths, nutrition_data, transform=None):
        self.image_paths = image_paths
        self.nutrition_data = nutrition_data
        self.transform = transform
    def __len__(self):
        return len(self.image_paths)
    # Transform image and map to nutritional value
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        nutrition = torch.tensor(self.nutrition_data[idx], dtype=torch.float32)
        return image, nutrition

# Split the dataset
image_paths_train, image_paths_val, nutrition_data_train, nutrition_data_val = train_test_split(
    image_paths, nutrition_data, test_size=0.2, random_state=42)
# Create datasets and dataloaders
train_dataset = FoodDataset(image_paths_train, nutrition_data_train, transform)
val_dataset = FoodDataset(image_paths_val, nutrition_data_val, transform)
train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_dataloader = DataLoader(val_dataset, batch_size=32, shuffle=False)

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
    
device = "cuda" if torch.cuda.is_available() else "cpu"

# Instantiate the model
model = NutritionPredictor().to(device)
model.to(device)

# Define loss function and optimizer
criterion = nn.SmoothL1Loss()                                       # Huber loss is less sensitive to outliers
optimizer = Adam(model.parameters(), lr=0.0001, weight_decay=1e-5)  # Added weight decay
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.1, patience=2)

# If model doesn't improve for 5 epochs → Stop training
patience = 5
best_val_loss = float('inf')
epochs_without_improvement = 0
num_epochs = 30  

# TRAINING...
for epoch in range(num_epochs):
    print("Starting...")
    model.train()
    running_loss = 0.0
    for images, labels in train_dataloader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    # Calculate average training loss
    train_loss = running_loss/len(train_dataloader)
    # Validation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for images, labels in val_dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            val_loss += criterion(outputs, labels).item()
    val_loss /= len(val_dataloader)
    scheduler.step(val_loss)  # Update learning rate
    
    print(f"Epoch [{epoch+1}/{num_epochs}]")
    print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
    print(f"Current LR: {optimizer.param_groups[0]['lr']:.2e}")
    
    # Early stopping check
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        epochs_without_improvement = 0
        torch.save(model.state_dict(), "best_model.pth")
    else:
        epochs_without_improvement += 1
        if epochs_without_improvement >= patience:
            print("Early stopping triggered!")
            break

print("Training complete!")