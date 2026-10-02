FROM python:3.11-slim

WORKDIR /app

# Install only essential packages to keep image small
RUN pip install --no-cache-dir numpy

# Create a non-root user for security
RUN useradd -m -u 1000 sandboxuser

# Set the user
USER sandboxuser

# Run Python code from mounted volume
CMD ["python3", "-u", "/app/code.py"]

