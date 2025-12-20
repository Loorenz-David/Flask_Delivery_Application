#!/bin/bash
set -e

echo "Applying Eventlet monkey patch early..."

printf "import eventlet\neventlet.monkey_patch()" > /opt/python/run/patch.py

echo "Monkey patch file created at /opt/python/run/patch.py"