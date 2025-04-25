FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt
RUN pip install --no-cache-dir boto3

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8003

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]