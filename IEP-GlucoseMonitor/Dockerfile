FROM python:3.10-slim

WORKDIR /app

# 1) Copy and install pinned deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy your code + model
COPY . .

EXPOSE 8004

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]