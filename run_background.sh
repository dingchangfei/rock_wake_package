#!/bin/bash
# 使用 nohup 在后台运行（简单方式）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting in background with nohup..."
nohup python3 listen_rock.py > /tmp/rockwake_nohup.out 2>&1 &

PID=$!
echo "Process started with PID: $PID"
echo "Logs: /tmp/rockwake_nohup.out"
echo ""
echo "To stop: kill $PID"
echo "To check: ps aux | grep listen_rock"

