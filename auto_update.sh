#!/bin/bash

# --- 严格锁定配置 ---
PROJECT_DIR="/var/www/task-incubator"
PYTHON_BIN="/root/flask_env/bin/python"
PORT=39001
LOG_FILE="/var/www/task-incubator/output.log"

# --- 延迟逻辑 ---
# 如果脚本是由系统开机触发的（我们可以加个参数判断），则延迟 600 秒（10分钟）
if [ "$1" == "boot" ]; then
    echo "$(date): 系统刚启动，脚本进入10分钟等待状态..." >> /var/www/task-incubator/auto_check.log
    sleep 600
fi

cd $PROJECT_DIR

# 1. 检查远程更新
git fetch origin main

# 2. 比较提交 ID
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then
    echo "$(date): 发现更新，正在同步..." >> $LOG_FILE
    git pull origin main

    # 3. 精确击杀 39001 端口进程
    fuser -k $PORT/tcp

    # 4. 启动项目
    nohup $PYTHON_BIN main.py > $LOG_FILE 2>&1 &
    echo "$(date): 更新完成，已重启。" >> $LOG_FILE
else
    # 如果是因为开机启动运行到这里，虽然没更新，但也得把项目拉起来
    # 检查 39001 是否已经在运行，没运行就启动
    if ! lsof -i:$PORT > /dev/null; then
        nohup $PYTHON_BIN main.py > $LOG_FILE 2>&1 &
        echo "$(date): 开机自启动项目成功。" >> $LOG_FILE
    else
        echo "$(date): 已经是最新且项目运行中，无需操作。" >> $LOG_FILE
    fi
fi