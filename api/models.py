
from api import db
from datetime import datetime

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    config = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='CREATED')
    output = db.Column(db.JSON, nullable=True)  # Output from the agent.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
