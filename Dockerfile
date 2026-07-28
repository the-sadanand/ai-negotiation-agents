# Start from a lightweight Python 3.11 image (slim = smaller, faster)
FROM python:3.11-slim

# Set /app as the working directory inside the container
WORKDIR /app

# Install curl (needed for container health checks)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first — Docker caches this layer
# So dependencies only re-install when requirements.txt changes
COPY requirements.txt .

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL project files into the container
COPY . .

# Tell Docker this container listens on port 8000
EXPOSE 8000

# Start the FastAPI app with Uvicorn
# --host 0.0.0.0 = accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]