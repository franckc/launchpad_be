import os
import sys
import argparse
import tempfile
import subprocess
import logging
from pathlib import Path

STAGING_ROOT_DIR = os.getenv("STAGING_ROOT_DIR", "/tmp")


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clone_repository(repo_url):
    """
    Clone a GitHub repository into a unique temporary staging directory.
    
    Args:
        repo_url (str): The URL of the GitHub repository to clone
        
    Returns:
        Path: The path to the staging directory containing the cloned repository
    """
    try:
        # Create a unique temporary staging directory
        staging_dir = tempfile.mkdtemp(dir=STAGING_ROOT_DIR, prefix="repo_staging_")
        logger.info(f"Created temporary staging directory: {staging_dir}")
        
        # Clone the repository into the staging directory
        logger.info(f"Cloning repository: {repo_url}")
        subprocess.run(["git", "clone", repo_url, staging_dir], 
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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Clone a GitHub repository into a temporary staging directory')
    parser.add_argument('repo_url', type=str, help='The URL of the GitHub repository to clone')
    args = parser.parse_args()
    
    try:
        # Clone the repository
        staging_dir = clone_repository(args.repo_url)
        print(f"Repository cloned successfully to: {staging_dir}")
        
        # Additional processing can be added here
        
    except Exception as e:
        logger.error(f"Failed to process repository: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
