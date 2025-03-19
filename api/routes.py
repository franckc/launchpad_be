from flask import request, jsonify
from api import app
from api.utils import create_error_response
from api.models import db, Agent
import logging
import os
from api.image.builder import build_image
from api.models import Image

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
        
        # Log the image creation request
        if not agent:
            return create_error_response(f"Agent with id {agent_id} not found", 404)

        github_url = agent.config.get('githubUrl')
        if not github_url:
            return create_error_response("Agent configuration missing githubUrl", 400)

        # Start the image creation process
        logger.info(f"Creating image for agent {agent_id} with repository URL {github_url}")
        image_name = build_image(github_url, agent_id)
        logger.info(f"Image creation done for agent {agent_id}. Image name: {image_name}")

        # Update the image status in the database
        image = Image(agent_id=agent_id, build_status="DONE", name=image_name)
        db.session.add(image)
        db.session.commit()
        logger.info(f"Image record created in database for agent {agent_id}")

        return jsonify({'status': 'CREATED', 'image_name': image_name})

    except ValueError as e:
        return create_error_response(str(e), 400)
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


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


@app.route('/api/agent/<agent_id>/run/start', methods=['POST'])
def start_agent(agent_id):
    """
    Get the status for a specific agent run.
    ---
    responses:
      200:
        description: Job status retrieved successfully
      404:
        description: Job not found
    """
    try:
        # Query the agent from the database
        agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
        
        if not agent:
            return create_error_response(f"Agent with id {agent_id} not found", 404)
            
        # TODO: implement logic to start the agent and return run_id
        status = "RUNNING"  # Placeholder for actual status
        return jsonify({'status': status, 'run_id': 'placeholder_run_id'})
        
    except Exception as e:
        return create_error_response(f"Internal server error: {str(e)}", 500)


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
