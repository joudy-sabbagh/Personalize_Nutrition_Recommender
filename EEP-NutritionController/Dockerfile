FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gdown

# Create Data-Processing directory structure
RUN mkdir -p /app/Data-Processing/Dataset

# Download necessary files from Google Drive with --remaining-ok flag to continue despite file limits
RUN gdown --folder --remaining-ok https://drive.google.com/drive/folders/1ClU-aYo6KBwwSY-9Fn6g5GDygr8xlRia -O /app/Data-Processing

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]