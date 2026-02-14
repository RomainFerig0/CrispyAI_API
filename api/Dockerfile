# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy the API code
COPY main.py .
COPY utils/ ./utils/
COPY models/ ./models/

# Initialize environmental variables
ENV API_SECRET=A
ENV API_PASSWORD=B
ENV API_EMAIL=C

# Expose port
EXPOSE 8080

# Run the API with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
