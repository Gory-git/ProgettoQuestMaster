"""
End-to-end test demonstrating complete game functionality
Creates a story, validates it, plays through it, and verifies goal is reached
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment
os.environ['DATABASE_URL'] = 'sqlite:///e2e_test.db'
os.environ['FLASK_ENV'] = 'testing'
os.environ['OPENAI_API_KEY'] = 'test-key'

from app import create_app, db
from app.models import Story, GameSession
from app.services.game_service import GameEngine
import json


# Complete working PDDL example - simple escape room
ESCAPE_ROOM_DOMAIN = """
(define (domain escape-room)
  (:requirements :strips :typing)
  (:types room item)
  (:predicates
    (at ?r - room)
    (has ?i - item)
    (at-item ?i - item ?r - room)
    (door-between ?r1 - room ?r2 - room)
    (door-locked ?r1 - room ?r2 - room)
    (unlocks ?i - item ?r1 - room ?r2 - room)
    (escaped)
  )
  
  (:action move
    :parameters (?from - room ?to - room)
    :precondition (and 
      (at ?from) 
      (door-between ?from ?to)
      (not (door-locked ?from ?to))
    )
    :effect (and 
      (not (at ?from)) 
      (at ?to)
    )
  )
  
  (:action pickup
    :parameters (?i - item ?r - room)
    :precondition (and 
      (at ?r) 
      (at-item ?i ?r)
    )
    :effect (and 
      (has ?i) 
      (not (at-item ?i ?r))
    )
  )
  
  (:action unlock-door
    :parameters (?i - item ?r1 - room ?r2 - room)
    :precondition (and 
      (has ?i)
      (unlocks ?i ?r1 ?r2)
      (door-locked ?r1 ?r2)
    )
    :effect (and
      (not (door-locked ?r1 ?r2))
      (not (door-locked ?r2 ?r1))
    )
  )
  
  (:action escape
    :parameters (?r - room)
    :precondition (at ?r)
    :effect (escaped)
  )
)
"""

ESCAPE_ROOM_PROBLEM = """
(define (problem escape-the-room)
  (:domain escape-room)
  (:objects
    cell corridor exit - room
    key - item
  )
  (:init
    (at cell)
    (at-item key cell)
    (door-between cell corridor)
    (door-between corridor cell)
    (door-between corridor exit)
    (door-between exit corridor)
    (door-locked cell corridor)
    (door-locked corridor cell)
    (unlocks key cell corridor)
  )
  (:goal
    (escaped)
  )
)
"""


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_create_story():
    """Test 1: Create a validated story with PDDL"""
    print_header("TEST 1: Creating Story with PDDL")
    
    app = create_app()
    
    with app.app_context():
        # Clean up
        Story.query.filter_by(title='Escape Room Adventure').delete()
        db.session.commit()
        
        # Create story
        story = Story(
            title='Escape Room Adventure',
            description='Escape from a locked room',
            lore_content='You wake up in a locked cell. Find the key and escape!',
            pddl_domain=ESCAPE_ROOM_DOMAIN,
            pddl_problem=ESCAPE_ROOM_PROBLEM,
            is_validated=True,
            status='validated'
        )
        
        db.session.add(story)
        db.session.commit()
        
        print(f"✅ Story created: ID={story.id}, Title='{story.title}'")
        print(f"   Status: {story.status}")
        print(f"   Validated: {story.is_validated}")
        
        return story.id


def test_initialize_game(story_id):
    """Test 2: Initialize game from PDDL"""
    print_header("TEST 2: Initializing Game Engine")
    
    app = create_app()
    
    with app.app_context():
        story = Story.query.get(story_id)
        
        # Create engine
        engine = GameEngine(story.pddl_domain, story.pddl_problem)
        
        print("✅ Game engine initialized")
        print(f"\n📊 Initial State ({len(engine.game_state.current_facts)} facts):")
        for fact in sorted(engine.game_state.current_facts):
            print(f"   • {fact}")
        
        print(f"\n🎯 Goal: {engine.parser.goal['positive']}")
        
        # Get available actions
        actions = engine.get_available_actions()
        print(f"\n🎮 Available Actions ({len(actions)}):")
        for action in actions:
            print(f"   • {action['display_text']}")
        
        return engine, actions


def test_play_to_completion(engine):
    """Test 3: Play through the game to completion"""
    print_header("TEST 3: Playing Through Game")
    
    # Optimal solution:
    # 1. pickup key cell
    # 2. unlock-door key cell corridor
    # 3. move cell corridor
    # 4. move corridor exit
    # 5. escape exit
    
    moves = [
        ('pickup', {'i': 'key', 'r': 'cell'}),
        ('unlock-door', {'i': 'key', 'r1': 'cell', 'r2': 'corridor'}),
        ('move', {'from': 'cell', 'to': 'corridor'}),
        ('move', {'from': 'corridor', 'to': 'exit'}),
        ('escape', {'r': 'exit'})
    ]
    
    for step_num, (action, bindings) in enumerate(moves, 1):
        print(f"\n--- Step {step_num} ---")
        
        # Get available actions
        actions = engine.get_available_actions()
        print(f"Available actions: {len(actions)}")
        
        # Find the action we want
        found = False
        for avail_action in actions:
            if avail_action['action'] == action and avail_action['bindings'] == bindings:
                print(f"⚡ Executing: {avail_action['display_text']}")
                result = engine.execute_action(action, bindings)
                found = True
                
                if result['goal_reached']:
                    print(f"\n🎉 GOAL REACHED IN {result['step']} STEPS!")
                    return True
                break
        
        if not found:
            print(f"❌ Action not available: {action} with {bindings}")
            return False
    
    print(f"\n❌ Goal not reached after {len(moves)} moves")
    return False


def test_api_game_session(story_id):
    """Test 4: Test game session via API"""
    print_header("TEST 4: Testing via API Endpoints")
    
    app = create_app()
    
    with app.app_context():
        client = app.test_client()
        
        # Create session
        print("\n1. Creating game session...")
        response = client.post(
            '/api/game/sessions',
            json={'story_id': story_id},
            content_type='application/json'
        )
        
        assert response.status_code == 201, f"Failed to create session: {response.get_json()}"
        data = response.get_json()
        session_id = data['session']['id']
        print(f"   ✅ Session created: ID={session_id}")
        print(f"   Available actions: {len(data['available_actions'])}")
        
        # Execute actions
        actions_sequence = [
            ('pickup', {'i': 'key', 'r': 'cell'}),
            ('unlock-door', {'i': 'key', 'r1': 'cell', 'r2': 'corridor'}),
            ('move', {'from': 'cell', 'to': 'corridor'}),
            ('move', {'from': 'corridor', 'to': 'exit'}),
            ('escape', {'r': 'exit'})
        ]
        
        for step, (action, bindings) in enumerate(actions_sequence, 1):
            print(f"\n{step}. Executing {action}...")
            response = client.post(
                f'/api/game/sessions/{session_id}/action',
                json={'action': action, 'bindings': bindings},
                content_type='application/json'
            )
            
            assert response.status_code == 200, f"Action failed: {response.get_json()}"
            data = response.get_json()
            
            print(f"   ✅ Step {data['session']['steps_taken']}")
            print(f"   Goal reached: {data['goal_reached']}")
            
            if data['goal_reached']:
                print(f"\n🎉 Game completed via API in {data['session']['steps_taken']} steps!")
                return True
        
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🎮 QUESTMASTER END-TO-END TEST")
    print("=" * 70)
    
    try:
        # Test 1: Create story
        story_id = test_create_story()
        
        # Test 2: Initialize engine
        engine, actions = test_initialize_game(story_id)
        
        # Test 3: Play to completion
        success = test_play_to_completion(engine)
        if not success:
            print("\n❌ Failed to complete game via engine")
            return False
        
        # Test 4: Test via API
        success = test_api_game_session(story_id)
        if not success:
            print("\n❌ Failed to complete game via API")
            return False
        
        print_header("✅ ALL TESTS PASSED!")
        print("\n🎉 The complete game engine is working correctly:")
        print("   • PDDL parsing ✓")
        print("   • State management ✓")
        print("   • Action calculation ✓")
        print("   • Precondition evaluation ✓")
        print("   • Effect application ✓")
        print("   • Goal checking ✓")
        print("   • API integration ✓")
        print("   • Database persistence ✓")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
