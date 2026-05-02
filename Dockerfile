# Use a slim Python image for a smaller footprint
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for compilation and git
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install 'uv' for ultra-fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy backend dependency files first to leverage Docker cache
# Note: We are in the root, so we copy from backend/
COPY backend/requirements.txt .

# Install Python dependencies using uv
RUN uv pip install --system -r requirements.txt

# Copy the backend source code
COPY backend/ .

# Expose the port (Azure App Service/Container Apps standard)
EXPOSE 8080

# Command to run the FastAPI application
# We use --host 0.0.0.0 to allow external access to the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
