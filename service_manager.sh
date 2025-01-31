#!/bin/bash

# 配置参数
FLASK_PORT=8080
FLASK_SCRIPT="app.py"
FLASK_LOG="flask_app.log"

DOCKER_PORT=8070
DOCKER_IMAGE="grobid/grobid:0.8.1"
CONTAINER_ID_FILE="grobid_container.id"  # 新增：容器ID存储文件

# GPU检测逻辑
check_gpu() {
    if command -v nvidia-smi &> /dev/null && nvidia-smi -L; then
        echo "GPU detected. Running Docker with GPU support..."
        GPU_FLAG="--gpus all"
    else
        echo "No GPU detected. Running Docker without GPU support..."
        GPU_FLAG=""
    fi
}

# 检查容器是否正在运行
is_container_running() {
    docker ps --filter "id=$1" --format "{{.ID}}" | grep -q .
}

# 优雅停止容器
stop_docker_grobid() {
    if [ -f "$CONTAINER_ID_FILE" ]; then
        local container_id=$(cat $CONTAINER_ID_FILE)
        if is_container_running $container_id; then
            echo "Stopping Grobid container $container_id..."
            docker stop $container_id >/dev/null
            echo "Grobid container stopped successfully"
        else
            echo "Grobid container not running"
        fi
        rm -f $CONTAINER_ID_FILE
    else
        echo "No recorded Grobid container found"
    fi
}

# 启动Grobid容器
start_docker_grobid() {
    echo "Starting Grobid service on port $DOCKER_PORT..."
    
    # 启动容器并记录ID
    local container_id=$(
        docker run -d \
        --rm \
        $GPU_FLAG \
        --init \
        --ulimit core=0 \
        -p $DOCKER_PORT:8070 \
        $DOCKER_IMAGE
    )
    
    # 保存容器ID到文件
    echo $container_id > $CONTAINER_ID_FILE
    echo "Grobid container started with ID: $container_id"
}

# 主控制逻辑
case "$1" in
    start)
        # 停止已有服务
        kill -9 $(lsof -ti :$FLASK_PORT) 2>/dev/null
        stop_docker_grobid
        
        # 启动服务
        check_gpu
        conda activate pdf
        start_docker_grobid
        nohup python3 $FLASK_SCRIPT > $FLASK_LOG 2>&1 &
        echo "All services started"
        ;;
    stop)
        kill -9 $(lsof -ti :$FLASK_PORT) 2>/dev/null
        stop_docker_grobid
        echo "All services stopped"
        ;;
    status)
        echo "=== Service Status ==="
        # 检查Flask
        if lsof -i :$FLASK_PORT >/dev/null; then
            echo "Flask: Running"
        else
            echo "Flask: Not running"
        fi
        
        # 检查Docker
        if [ -f "$CONTAINER_ID_FILE" ]; then
            container_id=$(cat $CONTAINER_ID_FILE)
            if is_container_running $container_id; then
                echo "Grobid: Running (Container ID: $container_id)"
            else
                echo "Grobid: Not running (Stale ID file)"
            fi
        else
            echo "Grobid: Not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
