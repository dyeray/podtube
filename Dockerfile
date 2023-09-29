FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Non-root user
USER www-data

# Expose the server port
EXPOSE 8080

# Command to start the server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
