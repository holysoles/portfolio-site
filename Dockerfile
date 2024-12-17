ARG BUILD_DATE

FROM python:3.10-slim

WORKDIR /app

ENV PORT 5000
ENV BUILD_DATE ${BUILD_DATE}

# Copy the necessary files and directories into the container
COPY static/ ./static/
COPY templates/ ./templates/
COPY blog/ ./blog/
COPY app.py requirements.txt  ./

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT}/tcp
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:${PORT}", "-w", "4"]
