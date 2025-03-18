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

def clone_repository(github_url):
    """
    Clone a GitHub repository into a unique temporary staging directory.
    
    Args:
        github_url (str): The URL of the GitHub repository to clone
        
    Returns:
        Path: The path to the staging directory containing the cloned repository
    """
    try:
        # Create a unique temporary staging directory
        staging_dir = tempfile.mkdtemp(dir=STAGING_ROOT_DIR, prefix="repo_staging_")
        logger.info(f"Created temporary staging directory: {staging_dir}")
        
        # Clone the repository into the staging directory
        logger.info(f"Cloning repository: {github_url}")
        subprocess.run(["git", "clone", github_url, staging_dir], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        
        logger.info(f"Successfully cloned repository to {staging_dir}")
        return Path(staging_dir)
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e.stderr.decode().strip()}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


def copy_supervisor_code(staging_dir):
    # Get the path to the supervisor directory in the current codebase
    current_dir = Path(__file__).parent.parent.parent  # Go up to the root of the codebase
    supervisor_dir = current_dir / "supervisor"
    
    if not supervisor_dir.exists():
        raise FileNotFoundError(f"Supervisor directory not found at {supervisor_dir}")
    
    # Create the destination directory in staging
    staging_supervisor_dir = staging_dir / "supervisor"
    staging_supervisor_dir.mkdir(exist_ok=True)
    
    # Copy supervisor files to staging directory
    logger.info(f"Copying supervisor code to {staging_supervisor_dir}")
    subprocess.run(["cp", "-r", f"{supervisor_dir}/.", f"{staging_supervisor_dir}/"], 
                    check=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
    
    logger.info(f"Successfully copied supervisor code to staging directory")

def update_pyproject(staging_dir):
    pyproject_path = staging_dir / "pyproject.toml"
    try:
        # Check if pyproject.toml exists
        if pyproject_path.exists():
            logger.info(f"Updating existing pyproject.toml at {pyproject_path}")
        with open(pyproject_path, "r") as f:
            content = f.read()
        
        # Check if the file uses TOML format
        try:
            # Parse the TOML content
            parsed_toml = tomli.loads(content)
            
            # Add flask to dependencies (create section if needed)
            if 'project' not in parsed_toml:
                parsed_toml['project'] = {}
            if 'dependencies' not in parsed_toml['project']:
                parsed_toml['project']['dependencies'] = []
            
            # Check if flask is already in dependencies
            dependencies = parsed_toml['project']['dependencies']
            if 'flask' not in [dep.split('>=')[0].strip() for dep in dependencies 
                if isinstance(dep, str)]:
                    dependencies.append('flask')
            
            # Write the updated TOML back
            with open(pyproject_path, "wb") as f:
                tomli_w.dump(parsed_toml, f)
            logger.info("Successfully added flask to project dependencies")
            
        except (tomli.TOMLDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse pyproject.toml: {str(e)}. Creating a new one.")
            _create_new_pyproject(pyproject_path)
        else:
            logger.info(f"No pyproject.toml found at {pyproject_path}. Creating a new one.")
        _create_new_pyproject(pyproject_path)

    except Exception as e:
        logger.error(f"Error updating pyproject.toml: {str(e)}")
        raise

    # Helper function to create a new pyproject.toml
    def _create_new_pyproject(path):
        with open(path, "w") as f:
            f.write("[project]\n")
            f.write("name = \"agent-with-supervisor\"\n")
            f.write("version = \"0.1.0\"\n")
            f.write("dependencies = [\"flask\"]\n")
        logger.info(f"Created new pyproject.toml at {path}")


def prepare_staging(staging_dir):
    """
    Copy the supervisor directory from the current codebase into the staging directory.
    Add a dependency on flask to the pyproject.toml file in the staging directory.
    
    Args:
        staging_dir (Path): Path to the staging directory
        
    Returns:
    """
    try:
        copy_supervisor_code(staging_dir)
        
        update_pyproject(staging_dir)
    
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
        
        logger.info(f"Docker image saved successfully to: {image_path}")
        return str(image_name)
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build Docker image: {e.stderr.decode().strip()}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while building image: {str(e)}")
        raise

# Main entry point method for building an image for an agent.
def build_image(github_url, agent_id):
    # Clone the repository
    logger.info(f"Cloning repository: {github_url}")
    staging_dir = clone_repository(github_url)
    logger.info(f"Repository cloned successfully to: {staging_dir}")
    
    # Prepare staging by adding the supervisor code
    logger.info("Preparing staging directory...")
    prepare_staging(staging_dir)
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
