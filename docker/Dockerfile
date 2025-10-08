# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
COPY .env .

# Install Python dependencies
RUN pip install  -r requirements.txt

# Copy the rest of the application code into the container
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Set the entrypoint to run your shell script
CMD ["bash", "/run.sh"]