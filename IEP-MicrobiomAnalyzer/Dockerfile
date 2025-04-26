FROM python:3.10-slim

WORKDIR /app

# 1) Copy and install pinned deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy your code + model
COPY . .

# Expose the port the app runs on
EXPOSE 8003

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]