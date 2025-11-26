#!/bin/bash
# 停止后台运行

PLIST_NAME="com.example.rockwake.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "Stopping LaunchAgent..."

# 卸载 LaunchAgent
if [ -f "$TARGET_PLIST" ]; then
    launchctl unload "$TARGET_PLIST" 2>/dev/null
    echo "LaunchAgent stopped!"
else
    echo "LaunchAgent not found. It may not be running."
fi

