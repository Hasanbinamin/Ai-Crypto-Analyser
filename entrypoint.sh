#!/bin/bash

# Start the FastAPI server in the background
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Wait for the API server to start
sleep 5

# Start the Telegram bot
python bot.py

# Keep the container running
wait
