"""
Game routes - Phase 2: Interactive Story Game endpoints
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import Story, GameSession
from app.services import NarrativeService
import json
import uuid
from datetime import datetime

bp = Blueprint('game', __name__)

# Initialize service
narrative_service = NarrativeService()


@bp.route('/game/sessions', methods=['POST'])
def create_game_session():
    """Start a new game session"""
    data = request.get_json()
    story_id = data.get('story_id')
    
    if not story_id:
        return jsonify({'error': 'story_id is required'}), 400
    
    story = Story.query.get_or_404(story_id)
    
    if not story.is_validated:
        return jsonify({'error': 'Story must be validated before playing'}), 400
    
    # Create session
    session = GameSession(
        story_id=story_id,
        session_key=str(uuid.uuid4()),
        current_state=json.dumps({'initial': True}),  # Placeholder for PDDL state
        action_history=json.dumps([]),
        narrative_history=json.dumps([])
    )
    
    db.session.add(session)
    db.session.commit()
    
    # Generate initial narrative
    initial_narrative = narrative_service.generate_narrative(
        story.lore_content,
        'Starting state of the adventure',
        None,
        ['Begin adventure']  # Initial action
    )
    
    # Generate image if enabled
    image_url = narrative_service.generate_image(initial_narrative, story.lore_content)
    
    return jsonify({
        'session': session.to_dict(),
        'narrative': initial_narrative,
        'image_url': image_url,
        'available_actions': narrative_service.format_actions_for_display(
            ['begin_adventure'],
            {'begin_adventure': 'Start your adventure'}
        )
    }), 201


@bp.route('/game/sessions/<int:session_id>', methods=['GET'])
def get_game_session(session_id):
    """Get game session details"""
    session = GameSession.query.get_or_404(session_id)
    story = Story.query.get(session.story_id)
    
    return jsonify({
        'session': session.to_dict(),
        'story': {
            'id': story.id,
            'title': story.title,
            'description': story.description
        }
    }), 200


@bp.route('/game/sessions/<int:session_id>/action', methods=['POST'])
def take_action(session_id):
    """Take an action in the game"""
    session = GameSession.query.get_or_404(session_id)
    story = Story.query.get(session.story_id)
    data = request.get_json()
    
    action = data.get('action')
    if not action:
        return jsonify({'error': 'action is required'}), 400
    
    try:
        # Get current state
        current_state = json.loads(session.current_state) if session.current_state else {}
        action_history = json.loads(session.action_history) if session.action_history else []
        narrative_history = json.loads(session.narrative_history) if session.narrative_history else []
        
        # In a full implementation, this would:
        # 1. Parse PDDL to get current valid actions
        # 2. Apply the action to update state
        # 3. Check if goal is reached
        
        # For now, simulate state progression
        action_history.append(action)
        session.steps_taken += 1
        
        # Generate available actions (simplified - would come from PDDL planner)
        available_actions = [
            'explore_north',
            'explore_south', 
            'talk_to_npc',
            'use_item'
        ]
        
        # Generate narrative for new state
        state_description = f"After {session.steps_taken} steps, having taken actions: {', '.join(action_history[-3:])}"
        narrative = narrative_service.generate_narrative(
            story.lore_content,
            state_description,
            action,
            available_actions
        )
        
        narrative_history.append({
            'step': session.steps_taken,
            'action': action,
            'narrative': narrative
        })
        
        # Generate image if enabled
        image_url = narrative_service.generate_image(narrative, story.lore_content)
        
        # Check for goal completion (simplified)
        is_completed = session.steps_taken >= story.depth_max
        
        if is_completed:
            session.is_completed = True
            session.completed_at = datetime.utcnow()
            narrative += "\n\n🎉 Congratulations! You have completed the quest!"
        
        # Update session
        session.current_state = json.dumps(current_state)
        session.action_history = json.dumps(action_history)
        session.narrative_history = json.dumps(narrative_history)
        session.last_action_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'session': session.to_dict(),
            'narrative': narrative,
            'image_url': image_url,
            'available_actions': narrative_service.format_actions_for_display(
                available_actions,
                {a: f"Choose to {a.replace('_', ' ')}" for a in available_actions}
            ),
            'is_completed': is_completed
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/game/sessions/<int:session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """Get the narrative history of a game session"""
    session = GameSession.query.get_or_404(session_id)
    
    return jsonify({
        'session_id': session.id,
        'narrative_history': json.loads(session.narrative_history) if session.narrative_history else [],
        'action_history': json.loads(session.action_history) if session.action_history else []
    }), 200


@bp.route('/game/sessions', methods=['GET'])
def list_game_sessions():
    """List all game sessions"""
    story_id = request.args.get('story_id', type=int)
    
    query = GameSession.query
    if story_id:
        query = query.filter_by(story_id=story_id)
    
    sessions = query.order_by(GameSession.started_at.desc()).all()
    
    return jsonify({
        'sessions': [session.to_dict() for session in sessions]
    }), 200


@bp.route('/game/sessions/<int:session_id>', methods=['DELETE'])
def delete_game_session(session_id):
    """Delete a game session"""
    session = GameSession.query.get_or_404(session_id)
    
    db.session.delete(session)
    db.session.commit()
    
    return jsonify({'message': 'Session deleted'}), 200
