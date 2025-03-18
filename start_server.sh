#!/bin/bash

if [ -n "$VIRTUAL_ENV" ]; then
  echo "Virtual environment is active: $VIRTUAL_ENV"
else
  echo "No virtual environment active. Run 'source .venv/bin/activate' to activate it."
  exit 1
fi

command="uv run python main.py"

log_file="main.log"

# Start the command with nohup and redirect stdout and stderr to the log file
nohup $command > "$log_file" 2>&1 &