from typing import Tuple, Any
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def create_error_response(message: str, status_code: int, log=True) -> Tuple[Any, int]:
    """Create a standardized error response."""
    if log:
        logger.error(f"Error: {message} (Status code: {status_code})")
    return jsonify({
        'error': message,
        'status_code': status_code
    }), status_code

def validate_job_id(job_id: str) -> bool:
    """Validate that a job ID is a valid integer."""
    try:
        int(job_id)
        return True
    except ValueError:
        return False