from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests

# Load model and processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Load image (replace with your own if needed)
img = Image.open("testing.png").convert("RGB")

# Generate caption
inputs = processor(images=img, return_tensors="pt")
out = model.generate(**inputs)
print("Caption:", processor.decode(out[0], skip_special_tokens=True))
