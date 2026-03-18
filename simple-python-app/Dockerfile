# simple-python-app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source
COPY . .

# Expose port and run the app
EXPOSE 5000
CMD ["python3", "app.py"]
