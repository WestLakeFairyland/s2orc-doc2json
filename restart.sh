#!/bin/bash

# Define variables
FLASK_PORT=8080
FLASK_SCRIPT="app.py"
FLASK_LOG="flask_app.log"

DOCKER_PORT=8070
DOCKER_IMAGE="grobid/grobid:0.8.1"

# Check if GPU is available
if command -v nvidia-smi &> /dev/null && nvidia-smi -L; then
    echo "GPU detected. Running Docker with GPU support..."
    GPU_FLAG="--gpus all"
else
    echo "No GPU detected. Running Docker without GPU support..."
    GPU_FLAG=""
fi

conda activate pdf

# Function: Kill process on a specific port
kill_process() {
    local port=$1
    echo "Stopping any process on port $port..."
    lsof -i:$port | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null
    echo "Port $port is now free."
}

# Function: Start Flask service
start_flask() {
    echo "Starting Flask service on port $FLASK_PORT..."
    nohup python3 $FLASK_SCRIPT > $FLASK_LOG 2>&1 &
    echo "Flask service started with PID: $!"
}

# Function: Start Grobid Docker container
start_docker_grobid() {
    echo "Starting Grobid service on port $DOCKER_PORT..."
    # Run Docker with or without GPU
    docker run --rm $GPU_FLAG --init --ulimit core=0 -p $DOCKER_PORT:8070 $DOCKER_IMAGE &
    echo "Grobid service is running..."
}

# Stop any existing processes on ports 8080 & 8070
kill_process $FLASK_PORT
kill_process $DOCKER_PORT

# Start services
start_flask
start_docker_grobid

echo "All services have been started successfully!"
