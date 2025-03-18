import os
import time
import logging
import requests

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

while True:
    try:
        response = requests.get("http://localhost:8080/api/job/process")
        if response.status_code == 200:
            logging.info(f"Processed job ID {response.json()['job_id']}")
        elif response.status_code == 204:
            logging.info("No job to process")
        else:
            logging.error(f"Failed to process job: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logging.error(f"HTTP request failed: {e}")
    
    time.sleep(5)
