# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install git (required for dbt and potentially other tools)
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose the port for FastAPI later
EXPOSE 8000

# Command to run the application (keeping container alive for development)
CMD ["tail", "-F", "/dev/null"]