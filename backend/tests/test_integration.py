"""
Integration test for game engine with database
Tests the complete flow from story creation to gameplay
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment before importing app
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['DATABASE_URL'] = 'sqlite:///test_integration.db'
os.environ['FLASK_ENV'] = 'testing'

from app import create_app, db
from app.models import Story, GameSession
import json


# Sample PDDL for testing
SAMPLE_DOMAIN = """
(define (domain treasure-hunt)
  (:requirements :strips :typing)
  (:types location item)
  (:predicates
    (at ?l - location)
    (has ?i - item)
    (at-item ?i - item ?l - location)
    (connected ?l1 - location ?l2 - location)
    (locked ?l - location)
  )
  
  (:action move
    :parameters (?from - location ?to - location)
    :precondition (and (at ?from) (connected ?from ?to) (not (locked ?to)))
    :effect (and (not (at ?from)) (at ?to))
  )
  
  (:action pickup
    :parameters (?i - item ?l - location)
    :precondition (and (at ?l) (at-item ?i ?l))
    :effect (and (has ?i) (not (at-item ?i ?l)))
  )
  
  (:action unlock
    :parameters (?key - item ?l - location)
    :precondition (and (has ?key) (locked ?l))
    :effect (not (locked ?l))
  )
)
"""

SAMPLE_PROBLEM = """
(define (problem find-treasure)
  (:domain treasure-hunt)
  (:objects
    entrance hall treasure-room - location
    key treasure - item
  )
  (:init
    (at entrance)
    (at-item key entrance)
    (at-item treasure treasure-room)
    (connected entrance hall)
    (connected hall entrance)
    (connected hall treasure-room)
    (connected treasure-room hall)
    (locked treasure-room)
  )
  (:goal
    (and (has treasure))
  )
)
"""


def test_story_creation():
    """Test creating a story with PDDL"""
    print("\n📝 Testing Story Creation...")
    
    app = create_app()
    
    with app.app_context():
        # Clean up any existing test data
        Story.query.filter_by(title='Test Treasure Hunt').delete()
        db.session.commit()
        
        # Create a new story
        story = Story(
            title='Test Treasure Hunt',
            description='A test adventure to find treasure',
            lore_content='Find the treasure in the locked room',
            pddl_domain=SAMPLE_DOMAIN,
            pddl_problem=SAMPLE_PROBLEM,
            is_validated=True,
            status='validated',
            branching_factor_min=2,
            branching_factor_max=4,
            depth_min=3,
            depth_max=10
        )
        
        db.session.add(story)
        db.session.commit()
        
        print(f"  ✅ Story created with ID: {story.id}")
        return story.id
    
    return None


def test_game_session_creation(story_id):
    """Test creating a game session"""
    print("\n🎮 Testing Game Session Creation...")
    
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        # Create game session
        response = client.post(
            '/api/game/sessions',
            json={'story_id': story_id},
            content_type='application/json'
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.get_json()}"
        data = response.get_json()
        
        assert 'session' in data, "Response missing 'session'"
        assert 'available_actions' in data, "Response missing 'available_actions'"
        
        session_id = data['session']['id']
        actions = data['available_actions']
        
        print(f"  ✅ Session created with ID: {session_id}")
        print(f"  📊 {len(actions)} initial actions available")
        
        if actions:
            print(f"  Example action: {actions[0]['display_text']}")
        
        return session_id, actions


def test_action_execution(session_id, action):
    """Test executing an action"""
    print(f"\n⚡ Testing Action Execution: {action['display_text']}...")
    
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        # Execute action
        response = client.post(
            f'/api/game/sessions/{session_id}/action',
            json={
                'action': action['action'],
                'bindings': action['bindings']
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.get_json()}"
        data = response.get_json()
        
        assert 'session' in data, "Response missing 'session'"
        assert 'available_actions' in data, "Response missing 'available_actions'"
        
        step = data['session']['steps_taken']
        new_actions = data['available_actions']
        goal_reached = data.get('goal_reached', False)
        
        print(f"  ✅ Action executed successfully")
        print(f"  📍 Now at step: {step}")
        print(f"  📊 {len(new_actions)} actions now available")
        print(f"  🎯 Goal reached: {goal_reached}")
        
        return new_actions, goal_reached


def test_complete_game_flow(story_id):
    """Test playing through a complete game"""
    print("\n🎲 Testing Complete Game Flow...")
    
    # Create session
    session_id, actions = test_game_session_creation(story_id)
    
    # Play through game
    max_steps = 15
    step = 0
    goal_reached = False
    
    while step < max_steps and not goal_reached and actions:
        print(f"\n  --- Step {step} ---")
        print(f"  Available actions: {len(actions)}")
        
        # Pick the first available action
        action = actions[0]
        print(f"  Executing: {action['display_text']}")
        
        # Execute action
        actions, goal_reached = test_action_execution(session_id, action)
        step += 1
        
        if goal_reached:
            print(f"\n  🎉 Goal reached in {step} steps!")
            break
    
    if not goal_reached and step >= max_steps:
        print(f"\n  ⚠️ Game not completed in {max_steps} steps")
    
    return goal_reached


def test_get_session(session_id):
    """Test retrieving session details"""
    print("\n📖 Testing Get Session...")
    
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        response = client.get(f'/api/game/sessions/{session_id}')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        
        assert 'session' in data, "Response missing 'session'"
        assert 'available_actions' in data, "Response missing 'available_actions'"
        
        print(f"  ✅ Retrieved session {session_id}")
        print(f"  📊 Session at step: {data['session']['steps_taken']}")
        
        return True


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🧪 Running Integration Tests")
    print("=" * 60)
    
    try:
        # Test 1: Create story
        story_id = test_story_creation()
        if not story_id:
            print("\n❌ Failed to create story")
            sys.exit(1)
        
        # Test 2: Create and retrieve session
        session_id, actions = test_game_session_creation(story_id)
        if not session_id:
            print("\n❌ Failed to create session")
            sys.exit(1)
        
        # Test 3: Get session details
        test_get_session(session_id)
        
        # Test 4: Execute a single action
        if actions:
            test_action_execution(session_id, actions[0])
        
        # Test 5: Complete game flow (new session)
        test_complete_game_flow(story_id)
        
        print("\n" + "=" * 60)
        print("✅ All integration tests passed!")
        print("=" * 60)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
