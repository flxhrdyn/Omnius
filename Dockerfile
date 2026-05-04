# --- Stage 1: Builder ---
# We use the full slim image to install dependencies that might need compilation
FROM python:3.12-slim AS builder

# Set the working directory
WORKDIR /app

# Install system dependencies required for compilation and git
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install 'uv' for ultra-fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy backend dependency files
COPY backend/requirements.txt .

# Install Python dependencies into a specific directory (/install)
# Using --no-cache to keep the builder stage small
RUN uv pip install --system -r requirements.txt

# --- Stage 2: Runner ---
# This is the final production image, kept as small as possible
FROM python:3.12-slim AS runner

# Set environment variables to optimize Python performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the installed packages from the builder stage
# Since we used --system in the builder, packages are in /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the backend source code
COPY backend/ .

# Expose the port (Azure App Service/Container Apps standard)
EXPOSE 8080

# Run the FastAPI server
# Using 0.0.0.0 to allow external access within the container network
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
