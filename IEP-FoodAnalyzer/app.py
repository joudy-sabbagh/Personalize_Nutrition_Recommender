from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# Load BLIP-2 model
processor = BlipProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Load image
image_path = "testing.png"
image = Image.open(image_path).convert("RGB")

# Use a strong prompt to force detailed caption
prompt = "Describe the dish in detail, listing all visible food items and their textures."

# Tokenize with prompt injection
inputs = processor(image, prompt, return_tensors="pt").to(device)

# Generate caption
out = model.generate(**inputs, max_length=50)
caption = processor.decode(out[0], skip_special_tokens=True)

print("Caption:", caption)
