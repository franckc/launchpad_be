import requests
import subprocess
import time
import logging

SUPERVISOR_PORT = 4000

# Utilities to manage docker containers.
# Calling the docker cli directly. In the future consider using a library like docker-py.

logger = logging.getLogger(__name__)

def get_running_container_info(image_name):
  """
  Check if a container is already running for the given image.
  Returns a tuple (container_id, port) where port is the host port mapped to container's port SUPERVISOR_PORT.
  """
  check_running = subprocess.run(
    ["docker", "ps", "--filter", f"ancestor={image_name}", "--format", "{{.ID}}"],
    capture_output=True,
    text=True,
    check=True
  )
  
  # If we find a running container, get its ID and mapped port
  if check_running.stdout.strip():
    container_id = check_running.stdout.strip()
    # Get the port mapping for this container
    port_result = subprocess.run(
      ["docker", "port", container_id, str(SUPERVISOR_PORT)],
      capture_output=True,
      text=True,
      check=True
    )
    # Extract the port number from output like "0.0.0.0:49153"
    port = port_result.stdout.strip().split(":")[-1]
    return (container_id, port)
  
  return None
    



# Check if a container is already running for the given image.
# If not, start a new container.
def get_or_start_container(image_name):
  """
  Start a container from the given image.
  Returns a tuple (container_id, port) where port is the host port mapped to container's port SUPERVISOR_PORT.
  """
  try:
    # First check if there is already a container running
    container_info = get_running_container_info(image_name)
    if container_info:
      return container_info
    
    # If not, start a new container.
    # Bind port SUPERVISOR_PORT of the container (supervisor port) to a random port on localhost
    start_result = subprocess.run(
      ["docker", "run", "-d", "-p", f":{SUPERVISOR_PORT}", image_name],
      capture_output=True,
      text=True,
      check=True
    )
    
    container_id = start_result.stdout.strip()
    # Get the port mapping for the new container
    port_result = subprocess.run(
      ["docker", "port", container_id, "4000"],
      capture_output=True,
      text=True,
      check=True
    )
    # Extract the port number from output
    port = port_result.stdout.strip().split(":")[-1]
    return (container_id, port)
    
  except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Failed to start container: {e}")

def wait_for_container_supervisor(supervisor_port):
  """
  Wait for the supervisor API to become available in the container.
  Timesout after 30 seconds, which indicates the container may not be healthy
  and an action should be attempted (stop + restart?) to recover.
  """
  supervisor_health_url = f"http://localhost:{supervisor_port}/api/health"
  
  timeout = 30
  start_time = time.time()
  
  while time.time() - start_time < timeout:
    try:
      response = requests.get(supervisor_health_url)
      if response.status_code == 200:
        logger.info("Supervisor API is healthy.")
        return
    except requests.ConnectionError:
      logger.warning("Connection error while waiting for supervisor API. Will retry...")
      pass
    
    time.sleep(1)
  
  raise RuntimeError("Supervisor API did not become available in time.")
