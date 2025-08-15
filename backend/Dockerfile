# Stage 1: Build stage for dependencies
FROM python:3.9-slim as builder

# Set environment variables to prevent generating .pyc files and to buffer output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---

# Stage 2: Final application stage
FROM python:3.9-slim

# Create the same non-root user as in the builder stage
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY ./app /app

# Use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Switch to the non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 