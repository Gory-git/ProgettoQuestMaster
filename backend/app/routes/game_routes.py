"""
Game routes - Phase 2: Interactive Story Game endpoints
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import Story, GameSession
from app.services import NarrativeService, GameEngine, GameState
import json
import uuid
from datetime import datetime

bp = Blueprint('game', __name__)

# Initialize service
narrative_service = NarrativeService()

# Store game engines for active sessions
# NOTE: This is an in-memory cache suitable for single-instance deployments.
# For production with multiple instances, use Redis or a similar distributed cache
# with proper serialization of GameEngine state. The current implementation is
# NOT thread-safe and should be protected with locks in multi-threaded environments.
_active_engines = {}


def _get_or_create_engine(session: GameSession, story: Story) -> GameEngine:
    """Get or create game engine for session"""
    session_key = session.session_key
    
    if session_key not in _active_engines:
        # Create new engine from PDDL
        try:
            engine = GameEngine(story.pddl_domain, story.pddl_problem)
            
            # Restore state if session has been played before
            if session.current_state:
                state_data = json.loads(session.current_state)
                if 'facts' in state_data:
                    engine.game_state = GameState.from_dict(state_data, engine.parser.goal)
            
            _active_engines[session_key] = engine
        except Exception as e:
            raise ValueError(f"Failed to initialize game engine: {str(e)}")
    
    return _active_engines[session_key]


@bp.route('/game/<int:story_id>/start', methods=['GET'])
def start_game(story_id):
    """Initialize game from PDDL files"""
    story = Story.query.get_or_404(story_id)
    
    if not story.is_validated:
        return jsonify({'error': 'Story must be validated before playing'}), 400
    
    if not story.pddl_domain or not story.pddl_problem:
        return jsonify({'error': 'Story missing PDDL files'}), 400
    
    try:
        # Create game engine
        engine = GameEngine(story.pddl_domain, story.pddl_problem)
        
        # Get initial game state
        initial_data = engine.initialize_game()
        
        return jsonify({
            'story_id': story_id,
            'initial_state': initial_data,
            'message': 'Game initialized successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to start game: {str(e)}'}), 500


@bp.route('/game/<int:story_id>/available-actions', methods=['GET'])
def get_available_actions_for_story(story_id):
    """Get applicable actions for a story (creates temporary engine)"""
    story = Story.query.get_or_404(story_id)
    
    if not story.is_validated:
        return jsonify({'error': 'Story must be validated before playing'}), 400
    
    try:
        # Create temporary engine
        engine = GameEngine(story.pddl_domain, story.pddl_problem)
        actions = engine.get_available_actions()
        
        return jsonify({
            'available_actions': actions,
            'count': len(actions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get actions: {str(e)}'}), 500


@bp.route('/game/<int:story_id>/goal-reached', methods=['GET'])
def check_goal_reached(story_id):
    """Check if goal state is reached (for a temporary engine)"""
    story = Story.query.get_or_404(story_id)
    
    if not story.is_validated:
        return jsonify({'error': 'Story must be validated'}), 400
    
    try:
        engine = GameEngine(story.pddl_domain, story.pddl_problem)
        goal_reached = engine.is_goal_reached()
        
        return jsonify({
            'goal_reached': goal_reached
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    
    if not story.pddl_domain or not story.pddl_problem:
        return jsonify({'error': 'Story missing PDDL files'}), 400
    
    try:
        # Create game engine
        engine = GameEngine(story.pddl_domain, story.pddl_problem)
        
        # Initialize game
        game_data = engine.initialize_game()
        
        # Create session
        session = GameSession(
            story_id=story_id,
            session_key=str(uuid.uuid4()),
            current_state=json.dumps(game_data['state']),
            action_history=json.dumps([]),
            narrative_history=json.dumps([])
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Store engine
        _active_engines[session.session_key] = engine
        
        # Generate initial narrative
        initial_narrative = narrative_service.generate_narrative(
            story.lore_content,
            'You begin your adventure',
            None,
            [a['display_text'] for a in game_data['available_actions'][:5]]
        )
        
        # Narrativize available action choices
        actions_to_show = game_data['available_actions']
        if actions_to_show:
            narrativized = narrative_service.narrativize_choices(
                story.lore_content,
                initial_narrative,
                [a['description'] for a in actions_to_show]
            )
            for i, action in enumerate(actions_to_show):
                action['display_text'] = narrativized[i]
        
        # Generate image if enabled
        image_url = narrative_service.generate_image(initial_narrative, story.lore_content)
        
        # Store initial narrative
        narrative_history = [{
            'step': 0,
            'narrative': initial_narrative,
            'image_url': image_url
        }]
        session.narrative_history = json.dumps(narrative_history)
        db.session.commit()
        
        return jsonify({
            'session': session.to_dict(),
            'narrative': initial_narrative,
            'image_url': image_url,
            'available_actions': game_data['available_actions']
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create session: {str(e)}'}), 500



@bp.route('/game/sessions/<int:session_id>', methods=['GET'])
def get_game_session(session_id):
    """Get game session details with current available actions"""
    session = GameSession.query.get_or_404(session_id)
    story = Story.query.get(session.story_id)
    
    try:
        # Get or create engine
        engine = _get_or_create_engine(session, story)
        
        # Get available actions
        available_actions = engine.get_available_actions() if not session.is_completed else []
        
        return jsonify({
            'session': session.to_dict(),
            'story': {
                'id': story.id,
                'title': story.title,
                'description': story.description
            },
            'available_actions': available_actions,
            'goal_reached': session.is_completed
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get session: {str(e)}'}), 500



@bp.route('/game/sessions/<int:session_id>/action', methods=['POST'])
def take_action(session_id):
    """Take an action in the game using PDDL game engine"""
    session = GameSession.query.get_or_404(session_id)
    story = Story.query.get(session.story_id)
    data = request.get_json()
    
    action_name = data.get('action')
    bindings = data.get('bindings', {})
    
    if not action_name:
        return jsonify({'error': 'action is required'}), 400
    
    try:
        # Get or create engine
        engine = _get_or_create_engine(session, story)
        
        # Execute action in game engine
        result = engine.execute_action(action_name, bindings)
        
        # Update session
        session.steps_taken = result['step']
        session.current_state = json.dumps(result['state'])
        
        # Update action history
        action_history = json.loads(session.action_history) if session.action_history else []
        action_history.append({
            'action': action_name,
            'bindings': bindings,
            'step': result['step']
        })
        session.action_history = json.dumps(action_history)
        
        # Generate narrative for the new state
        state_description = f"Step {result['step']}: Action taken - {action_name}"
        available_action_names = [a['display_text'] for a in result['available_actions'][:5]]
        
        narrative = narrative_service.generate_narrative(
            story.lore_content,
            state_description,
            action_name,
            available_action_names
        )
        
        # Narrativize available action choices
        actions_to_show = result['available_actions']
        if actions_to_show:
            narrativized = narrative_service.narrativize_choices(
                story.lore_content,
                narrative,
                [a['description'] for a in actions_to_show]
            )
            for i, action in enumerate(actions_to_show):
                action['display_text'] = narrativized[i]
        
        # Generate image if enabled
        image_url = narrative_service.generate_image(narrative, story.lore_content)
        
        # Update narrative history
        narrative_history = json.loads(session.narrative_history) if session.narrative_history else []
        narrative_history.append({
            'step': result['step'],
            'action': action_name,
            'narrative': narrative,
            'image_url': image_url
        })
        session.narrative_history = json.dumps(narrative_history)
        
        # Check for goal completion
        is_completed = result['goal_reached']
        
        if is_completed:
            session.is_completed = True
            session.completed_at = datetime.utcnow()
            narrative += "\n\n🎉 Congratulations! You have completed the quest!"
        
        # Update timestamp
        session.last_action_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'session': session.to_dict(),
            'narrative': narrative,
            'image_url': image_url,
            'available_actions': result['available_actions'],
            'is_completed': is_completed,
            'goal_reached': is_completed
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to execute action: {str(e)}'}), 500


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
