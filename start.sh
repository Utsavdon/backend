#!/bin/sh

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI app using Uvicorn
# Use $PORT if provided by the environment (Render sets PORT), default to 8000 otherwise.
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
