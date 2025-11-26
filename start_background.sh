#!/bin/bash
# 后台启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/launchagent/com.example.rockwake.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.example.rockwake.plist"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "Installing LaunchAgent..."

# 检测 Python3 路径
PYTHON3_PATH=$(which python3)
if [ -z "$PYTHON3_PATH" ]; then
    echo "Error: python3 not found!"
    exit 1
fi

echo "Using Python: $PYTHON3_PATH"

# 确保 LaunchAgents 目录存在
mkdir -p "$LAUNCH_AGENTS_DIR"

# 更新 plist 文件中的路径和 Python 路径
sed -e "s|SCRIPT_DIR|$SCRIPT_DIR|g" \
    -e "s|PYTHON_PATH|$PYTHON3_PATH|g" \
    -e "s|USER_HOME|$HOME|g" \
    "$PLIST_FILE" > "$TARGET_PLIST"

# 先卸载（如果已存在）
launchctl unload "$TARGET_PLIST" 2>/dev/null

# 加载 LaunchAgent
launchctl load "$TARGET_PLIST"

if [ $? -eq 0 ]; then
    echo "LaunchAgent installed and started!"
    echo "Logs: /tmp/rockwake.out.log and /tmp/rockwake.err.log"
    echo ""
    echo "To stop: ./stop_background.sh"
    echo "To check status: launchctl list | grep rockwake"
    echo "To view logs: tail -f /tmp/rockwake.out.log"
else
    echo "Error: Failed to load LaunchAgent"
    echo "Check logs: tail -f /tmp/rockwake.err.log"
    exit 1
fi

