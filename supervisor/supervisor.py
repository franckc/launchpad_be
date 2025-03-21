import logging
import os
import subprocess
from flask import Flask, request, jsonify

SUPERVISOR_PORT = 4000

app = Flask(__name__)

logger = logging.getLogger(__name__)


# Figure out the runs root dir. This is where the agent will store its data and run logs.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
runs_path = os.path.join(parent_dir, "runs")

@app.route('/api/run/<run_id>/start', methods=['POST'])
def start_agent(run_id):
  logger.info(f"Starting run id {run_id} of agent")

  # Parse the incoming JSON request
  logger.info(f"Request: {request}")
  data = request.get_json()
  
  # Extract the required fields
  envs = data.get('envs', {})
  inputs = data.get('inputs', {})

  # Log or use the extracted data
  logger.info(f"Environment variables: {envs}")
  logger.info(f"Inputs: {inputs}")
  
  # Prepare the command
  command = [
    "uv", "run", "launcher.py",
    "--command", "run",
    "--run_id", str(run_id),
    "--runs_root_dir", str(runs_path)
  ]

  # Add environment variables as arguments
  for key, value in envs.items():
    command.append("--env")
    command.append(f"{key}={value}")

  # Add inputs as arguments
  for key, value in inputs.items():
    command.append("--input")
    command.append(f"{key}={value}")

  # FIXME: do not log sensitive information
  logger.info(f"Command to execute: {command}")

  # Start the subprocess
  # Start the subprocess (non-blocking)
  process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
  )
  
  # Get the process ID
  pid = process.pid
  
  # Return the process ID in the response
  return jsonify({"status": "success", "message": "Agent started", "pid": pid})


@app.route('/api/run/<run_id>/stop', methods=['POST'])
def stop_agent(run_id):
  logger.info(f"Stopping agent with run id {run_id}")
  # TODO: Implement agent stop logic
  return jsonify({"status": "success", "message": "Agent stopped"})

@app.route('/api/run/<run_id>/status', methods=['GET'])
def agent_status(run_id):
  logger.info(f"Checking status for run id {run_id}")
  # TODO: Implement agent status checking logic
  return jsonify({"status": "running"})

@app.route('/api/run/<run_id>/output', methods=['GET'])
def agent_logs(run_id):
  logger.info(f"Retrieving output for run id {run_id}")

  # Construct the paths to log files
  stdout_log_path = os.path.join(runs_path, run_id, "stdout.log")
  stderr_log_path = os.path.join(runs_path, run_id, "stderr.log")

  # Initialize log content
  stdout_content = ""
  stderr_content = ""

  # Read stdout.log if it exists
  if os.path.exists(stdout_log_path):
    try:
      with open(stdout_log_path, 'r') as f:
        stdout_content = f.read()
    except Exception as e:
      logger.error(f"Error reading stdout log: {e}")

  # Read stderr.log if it exists
  if os.path.exists(stderr_log_path):
    try:
      with open(stderr_log_path, 'r') as f:
        stderr_content = f.read()
    except Exception as e:
      logger.error(f"Error reading stderr log: {e}")

  # Return the log contents
  return jsonify({"stdout": stdout_content, "stderr": stderr_content})

@app.route('/api/health', methods=['GET'])
def health_check():
  return jsonify({"status": "healthy"})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=SUPERVISOR_PORT, debug=True)