# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirments.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirments.txt

# Stage 2: Final stage
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
