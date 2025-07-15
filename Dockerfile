# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Update apt sources to use archive repositories for older Debian releases
RUN sed -i -E 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i -E 's|security.debian.org|archive.debian.org/debian-security|g' /etc/apt/sources.list

# Install system dependencies required for OpenCV (libGL.so.1, etc.), git, and GLib
# Corrected: Added libglib2.0-0
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libsm6 \
        libxrender1 \
        libglib2.0-0 \
        git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=600 -r requirements.txt # ADD --default-timeout=600

# Copy the rest of your application code to the container
COPY . .

# Expose the port for FastAPI later
EXPOSE 8000

# Command to keep the container alive for development
CMD ["tail", "-F", "/dev/null"]