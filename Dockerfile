# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port on which the FastAPI application will run (if applicable later)
# This is a placeholder for when we build the API
EXPOSE 8000

# Define environment variable for Python unbuffered output (good for logs)
ENV PYTHONUNBUFFERED 1

# Command to run your application - we'll update this later
# For now, it could be a placeholder or left out if docker-compose handles the entrypoint
# CMD ["python", "your_main_script.py"]