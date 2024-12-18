FROM python:3.10-slim

ARG BUILD_DATE

WORKDIR /app

# Copy the necessary files and directories into the container
COPY static/ ./static/
COPY templates/ ./templates/
COPY blog/ ./blog/
COPY app.py requirements.txt  ./

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV PORT=5000
ENV BUILD_DATE=$BUILD_DATE
ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:${PORT} --workers 4"
EXPOSE ${PORT}/tcp
CMD ["gunicorn", "app:app"]
