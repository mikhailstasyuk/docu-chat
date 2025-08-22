# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container to the root
WORKDIR /

# Set the PYTHONPATH environment variable
# This tells Python to look for packages in the root directory
ENV PYTHONPATH=/

# Copy the dependencies file
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application's code into a directory named 'app'
COPY ./app /app

# Command to run the application as a module
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]