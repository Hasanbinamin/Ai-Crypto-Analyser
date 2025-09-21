FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
# Install packages with increased timeout and retries
RUN pip install --no-cache-dir --timeout 1000 --retries 5 --upgrade pip
RUN pip install --no-cache-dir --timeout 1000 --retries 5 -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run both services using a script
COPY entrypoint.sh /entrypoint.sh
# Fix line endings and make executable
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
