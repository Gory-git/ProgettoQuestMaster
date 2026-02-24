"""
Game routes - Phase 2: Interactive Story Game endpoints
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import Story, GameSession
from app.services import NarrativeService, GameEngine, GameState
from app.services.game_service import humanize_pddl_action
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
                    engine.game_state = GameState.from_dict(state_data, engine.parser.goal, objects=engine.parser.objects)
            
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
        
        # Get initial game state (respect story branching factor)
        initial_data = engine.initialize_game(max_actions=story.branching_factor_max)
        
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
        actions = engine.get_available_actions(story.branching_factor_max)
        
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
        
        # Initialize game (respect story branching factor)
        game_data = engine.initialize_game(max_actions=story.branching_factor_max)
        
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

        # Sanity check: current_facts should NOT equal initial_state after step > 0
        if engine.game_state.step_count > 0:
            print(f"[DEBUG] Session {session_id} step={engine.game_state.step_count}, facts={len(engine.game_state.current_facts)}")

        # Get available actions (respect story branching factor)
        available_actions = engine.get_available_actions(story.branching_factor_max) if not session.is_completed else []

        # Narrativize choices using the last narrative from history
        if available_actions:
            narrative_history = json.loads(session.narrative_history) if session.narrative_history else []
            last_narrative = narrative_history[-1]['narrative'] if narrative_history else 'You begin your adventure'
            narrativized = narrative_service.narrativize_choices(
                story.lore_content,
                last_narrative,
                [a['description'] for a in available_actions]
            )
            for i, action in enumerate(available_actions):
                action['display_text'] = narrativized[i]
        
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
        
        # Sanity check: current_facts should NOT equal initial_state after step > 0
        if engine.game_state.step_count > 0:
            print(f"[DEBUG] Session {session_id} step={engine.game_state.step_count}, facts={len(engine.game_state.current_facts)}")

        # Save previous facts for delta computation
        previous_facts = set(engine.game_state.current_facts)

        # Execute action in game engine (respect story branching factor)
        result = engine.execute_action(action_name, bindings, max_actions=story.branching_factor_max)
        
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
        
        # Compute fact delta for richer narrative context
        result_facts = set(result['state'].get('facts', []))
        added_facts = result_facts - previous_facts
        removed_facts = previous_facts - result_facts
        humanized_action = humanize_pddl_action(
            f"{action_name} ({', '.join(bindings.values())})" if bindings else action_name
        )
        state_description = (
            f"Step {result['step']}: You performed '{humanized_action}'. "
            f"New facts: {', '.join(list(added_facts)[:10]) if added_facts else 'none'}. "
            f"No longer true: {', '.join(list(removed_facts)[:10]) if removed_facts else 'none'}."
        )
        available_action_names = [a['display_text'] for a in result['available_actions'][:5]]
        
        narrative = narrative_service.generate_narrative(
            story.lore_content,
            state_description,
            action_name,
            available_action_names,
            current_facts=list(result_facts),
            action_history=[h['action'] for h in result['state'].get('action_history', [])[-5:]]
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

        quest_summary = None
        if is_completed:
            session.is_completed = True
            session.completed_at = datetime.utcnow()

            # Build humanized action summary lines
            full_action_history = json.loads(session.action_history) if session.action_history else []
            full_narrative_history = json.loads(session.narrative_history) if session.narrative_history else []
            action_summary_lines = []
            for entry in full_action_history:
                action_nm = entry.get('action', '')
                binds = entry.get('bindings', {})
                step_n = entry.get('step', '?')
                humanized = humanize_pddl_action(
                    # Format: "action_name (param1, param2)" — matches humanize_pddl_action's expected input
                    f"{action_nm} ({', '.join(binds.values())})" if binds else action_nm
                )
                action_summary_lines.append(f"Step {step_n}: {humanized}")

            quest_summary = narrative_service.generate_quest_summary(
                lore=story.lore_content,
                story_title=story.title,
                narrative_history=full_narrative_history,
                action_summary_lines=action_summary_lines,
                steps_taken=result['step']
            )
            narrative = quest_summary

        # Update timestamp
        session.last_action_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'session': session.to_dict(),
            'narrative': narrative,
            'image_url': image_url,
            'available_actions': result['available_actions'],
            'is_completed': is_completed,
            'goal_reached': is_completed,
            'dead_end': result.get('dead_end', False),
            'quest_summary': quest_summary,
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
