from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/api/agent/start', methods=['POST'])
def start_agent():

  # Parse the incoming JSON request
  data = request.get_json()
  
  # Extract the config dictionary
  config = data.get('config', {})
  
  # Extract the required fields
  envs = config.get('envs', {})
  run_id = config.get('run_id')
  if (not run_id):
    return jsonify({"status": "error", "message": "Run ID not provided"})

  # Log or use the extracted data
  print(f"Starting run id {run_id} of agent")
  print(f"Environment variables: {envs}")
  
  # Prepare the command
  current_dir = os.path.dirname(os.path.abspath(__file__))
  parent_dir = os.path.dirname(current_dir)
  runs_path = os.path.join(parent_dir, "runs")
  command = ["uv", "run", "launcher.py", "--command", "run", "--run_id", run_id, "--runs_root_dir", runs_path]

  # Add environment variables as arguments
  for key, value in envs.items():
    command.append("--env")
    command.append(f"{key}={value}")

  # FIXME: do not log sensitive information
  print("Command to execute:", command)

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


@app.route('/api/agent/stop', methods=['POST'])
def stop_agent():
  # TODO: Implement agent stop logic
  return jsonify({"status": "success", "message": "Agent stopped"})

@app.route('/api/agent/status', methods=['GET'])
def agent_status():
  # TODO: Implement agent status checking logic
  return jsonify({"status": "running"})

@app.route('/api/agent/logs', methods=['GET'])
def agent_logs():
  # TODO: Implement agent logs retrieval logic
  return jsonify({"logs": []})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=4000, debug=True)