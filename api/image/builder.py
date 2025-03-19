import os
import sys
import argparse
import tempfile
import subprocess
import logging
from pathlib import Path
import tomli_w
import tomli

STAGING_ROOT_DIR = os.getenv("STAGING_ROOT_DIR")
if (STAGING_ROOT_DIR is None):
    raise ValueError("STAGING_ROOT_DIR environment variable is not set.")

IMAGES_ROOT_DIR = os.getenv("IMAGES_ROOT_DIR")
if (IMAGES_ROOT_DIR is None):
    raise ValueError("IMAGES_ROOT_DIR environment variable is not set.")


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Clone the agent repo to the staging/agent directory
def clone_repository(staging_dir, github_url):
    """
    Clone a GitHub repository into a unique temporary staging directory.
    
    Args:
        github_url (str): The URL of the GitHub repository to clone
        
    Returns:
        Path: The path to the staging directory containing the cloned repository
    """
    try:
        staging_agent_dir = Path(staging_dir) / "agent"
        staging_agent_dir.mkdir(exist_ok=True)

        # Clone the repository into the agent staging directory
        logger.info(f"Cloning repository: {github_url}")
        subprocess.run(["git", "clone", github_url, str(staging_agent_dir)], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        
        logger.info(f"Successfully cloned repository to {staging_agent_dir}")
        return staging_agent_dir
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e.stderr.decode().strip()}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


def add_supervisor(staging_dir):
    """
    Clone a GitHub repository into a unique temporary staging directory.
    
    Args:
        staging_dir (Path): Path to the staging directory
        
    Returns:
    """
    try:
        current_dir = Path(__file__).parent.parent.parent  # Go up to the root of the codebase
        supervisor_dir = current_dir / "supervisor"
        
        if not supervisor_dir.exists():
            raise FileNotFoundError(f"Supervisor directory not found at {supervisor_dir}")
        
        # Create the destination directory in staging
        staging_supervisor_dir = Path(staging_dir) / "supervisor"
        staging_supervisor_dir.mkdir(exist_ok=True)
        
        # Copy supervisor files to staging directory
        logger.info(f"Copying supervisor code to {staging_supervisor_dir}")
        subprocess.run(["cp", "-r", f"{supervisor_dir}/.", f"{staging_supervisor_dir}/"], 
                        check=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        logger.info(f"Successfully copied supervisor code to staging directory")
        return staging_supervisor_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to copy supervisor code: {e.stderr.decode().strip()}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while preparing staging: {str(e)}")
        raise


def build_docker_image(staging_dir, agent_id):
    """
    Build a Docker image from the staging directory.
    
    Args:
        staging_dir (Path): Path to the staging directory
        agent_id (int): The ID of the agent
        
    Returns:
        str: The name of the built Docker image
    """
    try:
        image_name = f"agent_image_{agent_id}"
        image_path = Path(IMAGES_ROOT_DIR) / f"{image_name}.tar"
        
        # Get the directory containing this script for the Dockerfile
        dockerfile_dir = Path(__file__).parent
        
        logger.info(f"Building Docker image with name: {image_name}")
        
        # Build the Docker image
        subprocess.run(
            ["docker", "build", 
                "-t", image_name, 
                "-f", f"{dockerfile_dir}/Dockerfile", 
                staging_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # For now store the image on disk but later push to a registry
        # TODO: may not be necessary to specify saving to disk. by default docker saves under /var/lib/docker on Linux.
        # Path(IMAGES_ROOT_DIR).mkdir(exist_ok=True, parents=True)
        
        # logger.info(f"Saving Docker image to: {image_path}")
        # subprocess.run(
        #     ["docker", "save", "-o", str(image_path), image_name],
        #     check=True,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE
        # )
        #logger.info(f"Docker image saved successfully to: {image_path}")
        return str(image_name)
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build Docker image: {e.stderr.decode().strip()}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while building image: {str(e)}")
        raise

# Main entry point method for building an image for an agent.
def build_image(github_url, agent_id):

    # Create a unique temporary staging directory
    staging_dir = tempfile.mkdtemp(dir=STAGING_ROOT_DIR, prefix="repo_staging_")
    logger.info(f"Created temporary staging directory: {staging_dir}")

    # Clone the repository
    logger.info(f"Cloning repository: {github_url}")
    agent_dir = clone_repository(staging_dir, github_url)
    logger.info(f"Repository cloned successfully to: {agent_dir}")
    
    # Add the supervisor code to staging
    logger.info("Preparing staging directory...")
    add_supervisor(staging_dir)
    logger.info(f"Supervisor code staged at: {staging_dir}")

    # Build the Docker image
    logger.info("Building Docker image...")
    image_name = build_docker_image(staging_dir, agent_id)
    logger.info(f"Docker image built and saved with name: {image_name}")

    return image_name


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Clone a GitHub repository into a temporary staging directory')
    parser.add_argument('github_url', type=str, help='The URL of the GitHub repository to clone')
    parser.add_argument('agent_id', type=int, help='The ID of the agent to create an image for')
    args = parser.parse_args()
    
    try:
        build_image(args.github_url, args.agent_id)
    except Exception as e:
        logger.error(f"Failed to process repository: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
