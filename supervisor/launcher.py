# Launcher for crew agent modules
# python launcher.py run --agent advanced_agent --env API_KEY=abc123 --env DEBUG=true


from dotenv import load_dotenv
import argparse
import sys
import os

# Load environment variables
load_dotenv()  


if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='VeritAI Agent Platform CLI')
    
    # Required command argument
    parser.add_argument('command', help='Command to execute (e.g., run, create, list)')
    
    # Optional arguments
    parser.add_argument('--agent', '-a', help='Agent module name to use')
    parser.add_argument('--env', '-e', action='append', metavar='KEY=VALUE', 
                        help='Environment variables to set (e.g., --env API_KEY=xyz)')
    
    args = parser.parse_args()
    
    # Process the arguments
    command = args.command
    agent_name = args.agent
    
    # Process environment variables if provided
    if args.env:
        for env_var in args.env:
            try:
                key, value = env_var.split('=', 1)
                os.environ[key] = value
                print(f"Set environment variable: {key}")
            except ValueError:
                print(f"Warning: Ignoring malformed environment variable: {env_var}")
    
    # Execute the command
    if command == 'run':
        if not agent_name:
            print("Error: The 'run' command requires an agent name. Use --agent to specify.")
            parser.print_help()
            sys.exit(1)
        
        print(f"Running agent: {agent_name}")
        try:
            # Dynamically import the agent's main run() function.
            module_name = agent_name + ".main"
            agent_module = __import__(module_name, globals(), locals(), fromlist=['run'])
            
            # Call the run function from the imported module
            if hasattr(agent_module, 'run'):
                agent_module.run()
            else:
                print(f"Error: The '{agent_name}.main' module does not have a 'run()' function.")
                sys.exit(1)
        except ImportError:
            print(f"Error: Could not import function '{agent_name}.main.run()'. Make sure it exists and is in the Python path.")
            sys.exit(1)
        except Exception as e:
            print(f"Error running agent '{agent_name}': {str(e)}")
            sys.exit(1)
        
    else:
        print(f"Unknown command: {command}")
        parser.print_help()
        sys.exit(1)
