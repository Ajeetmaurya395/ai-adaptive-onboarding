# Dockerfile for AI-Adaptive Onboarding Engine
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create data directory if it doesn't exist (though COPY should bring it)
RUN mkdir -p /app/data

# Expose Streamlit port
EXPOSE 8501

# Environment variables (placeholders, should be provided at runtime)
# ENV HF_TOKEN=your_token
# ENV MODEL_NAME=Qwen/Qwen2.5-7B-Instruct

# Run the application
CMD ["streamlit", "run", "app/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]