FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ app/
COPY templates/ templates/
COPY static/ static/ 2>/dev/null || true

# NOTE: This is for demonstration only. Running with debug=True in production is insecure!

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app/app.py"]
