# Use the official Python 3.8 slim image as the base image
FROM python:3.10-slim

WORKDIR /app

# Copy the necessary files and directories into the container
COPY static/ ./static/
COPY templates/ ./templates/
COPY blog/ ./blog/
COPY app.py requirements.txt  ./

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "4"]
