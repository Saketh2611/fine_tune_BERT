# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system tools
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 1. Install Dependencies (Optimized for Speed)
COPY requirements.txt .

# 🚨 MAGIC FIX: Install CPU-only PyTorch first (Saves ~2GB download)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install the rest (ignoring torch since we just installed it)
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the Application Code (Includes your local 'models' folder now!)
COPY . .

# 3. Build the Vector Database
# We SKIP 'setup_models.py' because we copied the models from your laptop
RUN python build_rag.py

# 4. Exposure
EXPOSE 8000

# 5. Runtime Command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]