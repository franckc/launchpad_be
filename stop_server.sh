#!/bin/bash

# Find the process ID of the process with "main.py" in its name
pid=$(pgrep -f main.py | tr '\n' ' ')

# Check if the process was found
if [ -n "$pid" ]; then
  # Send the terminate signal to the process
  kill -TERM $pid
  echo "Process main.py (PIDs: $pid) has been terminated."
else
  echo "No process with main.py found."
fi
