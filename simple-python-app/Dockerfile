# Use the latest patched slim Python 3.11 image
FROM python:3.11.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Upgrade pip & wheel and install dependencies
RUN python3 -m pip install --upgrade pip wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose app port
EXPOSE 5000

# Start the app
CMD ["python3", "app.py"]
