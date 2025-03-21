import logging
import requests
import traceback

from flask import request, jsonify
from api import app
from api.models import db, Image, Run, Agent
from api.image.builder import build_image
from api.container.manage import get_or_start_container
from api.utils import create_error_response
from sqlalchemy.orm.attributes import flag_modified


logger = logging.getLogger(__name__)

@app.route('/api/agent/<agent_id>/image/create', methods=['POST'])
def create_image(agent_id):
    """
    Create a new agent image. Get everything ready for running it.
    ---
    responses:
      200:
        description: Agent image creation successfull
      400:
        description: Invalid request parameters
    """
    try:
        if not request.is_json:
            return create_error_response("Request must be JSON", 400)

        # Read the agent configuration from the DB
        agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
        
        if not agent:
            return create_error_response(f"Agent with id {agent_id} not found", 404)

        github_url = agent.config.get('githubUrl')
        if not github_url:
            return create_error_response("Agent configuration missing githubUrl", 400)

        # Create a record in the database for the image
        image = Image(agent_id=agent_id, build_status="PENDING")
        db.session.add(image)
        db.session.commit()
        logger.info(f"Image record created in database for agent {agent_id}")

        # Start the image creation process
        try:
            logger.info(f"Creating image for agent {agent_id} with repository URL {github_url}")
            image_name, input_keys = build_image(github_url, agent_id, image.id)
            logger.info(f"Image creation done for agent {agent_id}. Image name: {image_name}")
            logger.info(f"Input keys extracted: {input_keys}")

            # Update the agent configuration with input_keys
            if agent.config is None:
              agent.config = {}
            agent.config['inputKeys'] = input_keys # Note: camelcase for JSON in DB as a convention
            # Flag the column as modified to ensure SQLAlchemy detects the change
            flag_modified(agent, 'config')
            db.session.commit()
            logger.info(f"Updated agent {agent_id} with inputKeys: {input_keys}")

            # Update the image name and status in the database
            image.name = image_name
            image.build_status = 'DONE'
            db.session.commit()
        except Exception as e:
            logger.error(f"Error building image for agent {agent_id}: {str(e)}")
            # Update image status to ERROR in the DB and return the error in the API response
            image.build_status = 'ERROR'
            db.session.commit()
            raise e

    except ValueError as e:
        return create_error_response(str(e), 400)
    except Exception as e:
        print(traceback.format_exc())
        return create_error_response(f"Internal server error: {str(e)}", 500)

    return jsonify({'status': 'DONE', 'imageName': image_name})


@app.route('/api/agent/<agent_id>/image/status', methods=['GET'])
def get_image_status(agent_id):
    """
    Get the status of an agent image creation process.
    ---
    responses:
      200:
        description: Image creation status retrieved successfully
      404:
        description: Agent not found or no active image creation process
    """
    try:
        # Query the agent from the database
        agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
        
        if not agent:
            return create_error_response(f"Agent with id {agent_id} not found", 404)
            
        # TODO: implement logic to check image creation status
        # This could involve checking a status field in the agent record
        # or querying a separate image_build table
        
        # Placeholder for actual status check
        status = "IN_PROGRESS"  # Could be one of: PENDING, IN_PROGRESS, COMPLETED, FAILED
        progress = 75  # Optional: percentage complete
        
        return jsonify({
            'status': status,
            'progress': progress,
            'message': 'Building container image'
        })
        
    except Exception as e:
        logger.error(f"Error while checking image status: {str(e)}")
        return create_error_response(f"Internal server error: {str(e)}", 500)


@app.route('/api/agent/<agent_id>/input', methods=['GET'])
def get_agent_input(agent_id):
    """
    Get the input necessary to run a specific agent.
    """
    # TODO: implement logic to retrieve job status based on run_id
    status = "UNKNOWN" # Placeholder for actual status retrieval logic
    return jsonify({'status': status})

@app.route('/api/agent/<agent_id>/run/start', methods=['POST'])
def start_agent(agent_id):
    """
    Start an agent run
    ---
    responses:
      200:
        description: Job status retrieved successfully
      404:
        description: Job not found
    """
    try:
        if not request.is_json:
            return create_error_response("Request must be JSON", 400)
        # Extract the input data from the request
        data = request.get_json()
        if 'inputs' not in data:
          return create_error_response("Request must contain 'inputs' field", 400)
            
        inputs = data['inputs']
        logger.info(f"Received inputs for agent {agent_id}: {inputs}")

        # Query the agent from the database
        agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return create_error_response(f"Agent with id {agent_id} not found", 404)

        # Query the image from the database
        image = db.session.query(Image).filter(Image.agent_id == agent_id).first()
        if not image:
            return create_error_response(f"No image found for agent {agent_id}", 404)

        # Insert the run record into the database
        config = {
          'agent': agent.config,
          'inputs': inputs
        }
        run = Run(agent_id=agent_id, image_id=image.id, config=config, status="PENDING")
        db.session.add(run)
        db.session.commit()
        logger.info(f"Run record created in database for agent {agent_id}")

        # Bring up the container, if not already running        
        container_id, supervisor_port = get_or_start_container(image.name)
        logger.info(f"Container {container_id} with supervisor port {supervisor_port} running for agent {agent_id}")

        # Call the supervisor API to start the agent run
        # Prepare the request payload with environment variables and inputs
        payload = {
          'envs': agent.config.get('envs', {}),
          'inputs': inputs
        }

        # Make the API request to the supervisor for starting the agent run.
        response = requests.post(f'http://localhost:{supervisor_port}/api/run/{run.id}/start', json=payload)
        if response.status_code != 200:
          run.status = 'ERROR'
          run.output = 'Error: ' + response.text
          db.session.commit()
          raise Exception(f"Failed to start agent run: {response.text}")

        # Update run status to RUNNING
        run.status = "RUNNING"
        db.session.commit()

        logger.info(f"Agent run {run.id} started successfully for agent {agent_id}")

    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)

    return jsonify({'status': 'RUNNING', 'runId': run.id})


@app.route('/api/agent/<agent_id>/run/<run_id>/status', methods=['GET'])
def get_run_status(agent_id, run_id):
    """
    Get the status for a specific agent run.
    ---
    responses:
      200:
        description: Job status retrieved successfully
      404:
        description: Job not found
    """
    # TODO: implement logic to retrieve job status based on run_id
    status = "UNKNOWN" # Placeholder for actual status retrieval logic
    return jsonify({'status': status})


# Returns the logs of an agent run
@app.route('/api/agent/<agent_id>/run/<run_id>/log', methods=['GET'])
def get_run_output(run_id):
    """
    Get the logs for a specific agent run.
    ---
    responses:
      200:
        description: Job output retrieved successfully
      404:
        description: Job not found
    """
    # TODO: implement logic to retrieve job output based on run_id
    output = "No output available" # Placeholder for actual output retrieval logic
    return jsonify({'output': output})


@app.errorhandler(404)
def not_found(error):
    return create_error_response("Resource not found", 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return create_error_response("Method not allowed", 405)

@app.errorhandler(500)
def internal_server_error(error):
    return create_error_response("Internal server error", 500)
