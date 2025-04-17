FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8000
EXPOSE 8000

# Command will be provided by smithery.yaml
CMD ["python", "anki_server.py"]