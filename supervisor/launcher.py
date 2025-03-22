# Launcher for crew agent modules.
# This is called by the supervisor to start a run of the agent.
# uv run python launcher.py run --agent advanced_agent --env API_KEY=abc123 --env DEBUG=true


#from dotenv import load_dotenv
import argparse
import sys
import os
import subprocess
from pathlib import Path
import json

# Load environment variables
#load_dotenv()  


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='VeritAI Agent Platform CLI')
    
    # Required command argument
    parser.add_argument('--command', metavar='KEY=VALUE', help='Command to execute (e.g., run)')
    parser.add_argument('--run_id', metavar='KEY=VALUE', help='ID of the run.')
    parser.add_argument('--runs_root_dir', metavar='KEY=VALUE', help='Root dir for storing run data.')

    # Optional arguments
    parser.add_argument('--env', action='append', metavar='KEY=VALUE', 
                        help='Environment variables to set (e.g., --env API_KEY=xyz)')
    parser.add_argument('--input', action='append', metavar='KEY=VALUE', 
                        help='Input for crew execution (e.g., --input topic=AI in healthcare)')

    args = parser.parse_args()
    
    # Process the arguments
    command = args.command
    run_id = args.run_id
    runs_root_dir = Path(args.runs_root_dir)

    # Process environment variables if provided
    if args.env:
        for env_var in args.env:
            try:
                key, value = env_var.split('=', 1)
                os.environ[key] = value
                print(f"Set environment variable: {key}")
            except ValueError:
                print(f"Warning: Ignoring malformed environment variable: {env_var}")

    # Process input data if provided
    inputs = {}
    if args.input:
        for input_var in args.input:
            try:
                key, value = input_var.split('=', 1)
                inputs[key] = value
                print(f"Received input: {key}={value}")
            except ValueError:
                print(f"Warning: Ignoring malformed input: {input_var}")

    # Execute the command
    if command == 'run':
        if not run_id:
            print("Error: --run_id cannot be empty")
            parser.print_help()
            sys.exit(1)

        # Ensure runs_root_dir is not empty
        if not runs_root_dir:
            print("Error: --runs_root_dir cannot be empty")
            parser.print_help()
            sys.exit(1)

        # Check if runs_root_dir exists, create if not
        if not os.path.exists(runs_root_dir):
            try:
                os.makedirs(runs_root_dir)
                print(f"Created directory: {runs_root_dir}")
            except OSError as e:
                print(f"Error creating directory {runs_root_dir}: {e}")
                sys.exit(1)

        print("Running agent...")
        # Create directory for run logs
        run_dir = os.path.join(runs_root_dir, run_id)
        os.makedirs(run_dir, exist_ok=True)

        # Define log file paths
        stdout_log = os.path.join(run_dir, "stdout.log")
        stderr_log = os.path.join(run_dir, "stderr.log")

        # Dump the input dictionary in a JSON file for the agent to read at startup
        inputs_file = os.path.join(run_dir, "inputs.json")
        with open(inputs_file, 'w') as f:
            json.dump(inputs, f, indent=2)

        # Start the subprocess
        agent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../agent")
        with open(stdout_log, 'w') as stdout_file, open(stderr_log, 'w') as stderr_file:
            # Create a copy of the current environment and add CREW_INPUT_JSON
            env = os.environ.copy()
            env['CREW_INPUT_JSON'] = inputs_file
            
            # Start the subprocess
            process = subprocess.Popen(
                ["uv", "run", "crewai", "run"],
                stdout=stdout_file,
                stderr=stderr_file,
                cwd=agent_dir,  # Note: we change the working directory to the agent directory
                env=env  # Pass the modified environment to the subprocess
            )
            
            # Get the PID of the process and store it in a file
            pid = process.pid
            pid_file = os.path.join(run_dir, "pid")
            with open(pid_file, 'w') as f:
                f.write(str(pid))
        
        # Note: we do not wait for the process to complete.
        # The supervisor will monitor the process and handle the completion.
        print(f"Agent execution started. Logs will be stored under {run_dir}")
        
    else:
        print(f"Unknown command: {command}")
        parser.print_help()
        sys.exit(1)
