FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir openai==0.28.0 python-dotenv

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8002

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]