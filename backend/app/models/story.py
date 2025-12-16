"""
Database models for QuestMaster application
"""

from datetime import datetime
from app import db
import json


class Story(db.Model):
    """
    Story model - represents a complete interactive story with PDDL and lore
    """
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Lore and metadata
    lore_content = db.Column(db.Text)  # Original lore document
    branching_factor_min = db.Column(db.Integer, default=2)
    branching_factor_max = db.Column(db.Integer, default=4)
    depth_min = db.Column(db.Integer, default=3)
    depth_max = db.Column(db.Integer, default=10)
    
    # PDDL files
    pddl_domain = db.Column(db.Text)  # PDDL domain file content
    pddl_problem = db.Column(db.Text)  # PDDL problem file content
    is_validated = db.Column(db.Boolean, default=False)
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, validated, published
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    game_sessions = db.relationship('GameSession', backref='story', lazy=True, cascade='all, delete-orphan')
    refinement_history = db.relationship('RefinementHistory', backref='story', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'lore_content': self.lore_content,
            'branching_factor_min': self.branching_factor_min,
            'branching_factor_max': self.branching_factor_max,
            'depth_min': self.depth_min,
            'depth_max': self.depth_max,
            'pddl_domain': self.pddl_domain,
            'pddl_problem': self.pddl_problem,
            'is_validated': self.is_validated,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RefinementHistory(db.Model):
    """
    Tracks the refinement iterations for PDDL generation
    """
    __tablename__ = 'refinement_history'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    iteration = db.Column(db.Integer, default=1)
    pddl_version = db.Column(db.Text)  # PDDL content at this iteration
    validation_errors = db.Column(db.Text)  # JSON string of validation errors
    reflection_feedback = db.Column(db.Text)  # Reflection agent's analysis
    author_response = db.Column(db.Text)  # Author's decision/modifications
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'story_id': self.story_id,
            'iteration': self.iteration,
            'pddl_version': self.pddl_version,
            'validation_errors': json.loads(self.validation_errors) if self.validation_errors else None,
            'reflection_feedback': self.reflection_feedback,
            'author_response': self.author_response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GameSession(db.Model):
    """
    Represents an active or completed game session (Phase 2)
    """
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    # Session data
    session_key = db.Column(db.String(100), unique=True, nullable=False)
    current_state = db.Column(db.Text)  # JSON string of current PDDL state
    action_history = db.Column(db.Text)  # JSON array of actions taken
    narrative_history = db.Column(db.Text)  # JSON array of narrative texts
    
    # Status
    is_completed = db.Column(db.Boolean, default=False)
    steps_taken = db.Column(db.Integer, default=0)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_action_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'story_id': self.story_id,
            'session_key': self.session_key,
            'current_state': json.loads(self.current_state) if self.current_state else None,
            'action_history': json.loads(self.action_history) if self.action_history else [],
            'narrative_history': json.loads(self.narrative_history) if self.narrative_history else [],
            'is_completed': self.is_completed,
            'steps_taken': self.steps_taken,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_action_at': self.last_action_at.isoformat() if self.last_action_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
