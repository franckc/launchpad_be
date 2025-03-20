import subprocess

# Utilties to manage docker containers.
# Calling the docker cli directly. In the future consider using a library like docker-py.

# Check if a container is already running for the given image.
# If not, start a new container.
def get_or_start_container(image_name):
  """
  Start a container from the given image.
  Returns a tuple (container_id, port) where port is the host port mapped to container's port 4000.
  """
  # Step 1: Check if there is already a container running for image with name image_name
  try:
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
        ["docker", "port", container_id, "4000"],
        capture_output=True,
        text=True,
        check=True
      )
      # Extract the port number from output like "0.0.0.0:49153"
      port = port_result.stdout.strip().split(":")[-1]
      return (container_id, port)
    
    # Step 2: Start a container if none is running
    # Bind port 4000 of the container (supervisor port) to a random port on localhost
    start_result = subprocess.run(
      ["docker", "run", "-d", "-p", ":4000", image_name],
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


