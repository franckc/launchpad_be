import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)

# Per Supabase doc, since the host is not IPV6, we use the transaction pooler mode.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': NullPool  # Important for transaction pooler mode
}

# Initialize database
db = SQLAlchemy(app)

# Import routes after app initialization to avoid circular imports
from api import routes

# We let the Next.js app handle DB migrations
#with app.app_context():
#    db.create_all()
