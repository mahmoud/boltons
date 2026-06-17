# Dockerfile for boltons development and testing
# Python 3.10 provides good compatibility with the codebase
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy the entire project into the container
COPY . .

# Install system dependencies (git is useful for development)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Install testing dependencies with pinned versions
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-cov==4.1.0

# Install boltons in editable mode
# This allows the tests to import boltons modules correctly
RUN pip install -e .

# Set environment variables for better Python behavior in containers
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command runs the test suite
CMD ["pytest", "tests/", "-v"]
