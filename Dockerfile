FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy only requirements to cache them in docker layer
COPY api/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY api/ ./api/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["sh", "-c", "cd api && uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
