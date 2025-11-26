#!/bin/bash
# 检查 LaunchAgent 状态

echo "=== LaunchAgent Status ==="
launchctl list | grep rockwake || echo "Not running"

echo ""
echo "=== Recent Logs (stdout) ==="
tail -20 /tmp/rockwake.out.log 2>/dev/null || echo "No stdout log"

echo ""
echo "=== Recent Logs (stderr) ==="
tail -20 /tmp/rockwake.err.log 2>/dev/null || echo "No stderr log"

