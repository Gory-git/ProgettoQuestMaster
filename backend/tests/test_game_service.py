"""
Tests for game service - PDDL parsing and game engine
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.game_service import PDDLParser, StateEvaluator, ActionCalculator, GameState, GameEngine


# Sample PDDL for testing
SAMPLE_DOMAIN = """
(define (domain simple-adventure)
  (:requirements :strips :typing)
  (:types location item)
  (:predicates
    (at ?l - location)
    (has ?i - item)
    (at-item ?i - item ?l - location)
    (connected ?l1 - location ?l2 - location)
  )
  
  (:action move
    :parameters (?from - location ?to - location)
    :precondition (and (at ?from) (connected ?from ?to))
    :effect (and (not (at ?from)) (at ?to))
  )
  
  (:action pickup
    :parameters (?i - item ?l - location)
    :precondition (and (at ?l) (at-item ?i ?l))
    :effect (and (has ?i) (not (at-item ?i ?l)))
  )
)
"""

SAMPLE_PROBLEM = """
(define (problem quest)
  (:domain simple-adventure)
  (:objects
    room1 room2 - location
    key sword - item
  )
  (:init
    (at room1)
    (at-item key room1)
    (at-item sword room2)
    (connected room1 room2)
    (connected room2 room1)
  )
  (:goal
    (and (has key) (has sword))
  )
)
"""


def test_pddl_parser():
    """Test PDDL parsing"""
    print("\n🔍 Testing PDDL Parser...")
    
    parser = PDDLParser(SAMPLE_DOMAIN, SAMPLE_PROBLEM)
    
    # Check actions parsed
    assert 'move' in parser.actions, "move action not found"
    assert 'pickup' in parser.actions, "pickup action not found"
    print(f"  ✅ Parsed {len(parser.actions)} actions")
    
    # Check objects parsed
    assert 'room1' in parser.objects, "room1 object not found"
    assert 'key' in parser.objects, "key object not found"
    print(f"  ✅ Parsed {len(parser.objects)} objects")
    
    # Check initial state
    assert len(parser.initial_state) > 0, "Initial state is empty"
    print(f"  ✅ Parsed initial state with {len(parser.initial_state)} facts")
    
    # Check goal
    assert 'positive' in parser.goal, "Goal not parsed"
    print(f"  ✅ Parsed goal with {len(parser.goal['positive'])} conditions")
    
    return True


def test_state_evaluator():
    """Test state evaluation"""
    print("\n🧪 Testing State Evaluator...")
    
    current_state = {'at room1', 'at-item key room1'}
    
    # Test positive precondition
    precondition = {'positive': ['at room1'], 'negative': []}
    bindings = {}
    result = StateEvaluator.evaluate_precondition(precondition, current_state, bindings)
    assert result == True, "Positive precondition evaluation failed"
    print("  ✅ Positive precondition evaluation works")
    
    # Test negative precondition
    precondition = {'positive': ['at room1'], 'negative': ['at room2']}
    result = StateEvaluator.evaluate_precondition(precondition, current_state, bindings)
    assert result == True, "Negative precondition evaluation failed"
    print("  ✅ Negative precondition evaluation works")
    
    # Test failing precondition
    precondition = {'positive': ['at room2'], 'negative': []}
    result = StateEvaluator.evaluate_precondition(precondition, current_state, bindings)
    assert result == False, "Failing precondition should return False"
    print("  ✅ Failing precondition correctly rejected")
    
    return True


def test_action_calculator():
    """Test action calculation"""
    print("\n⚙️ Testing Action Calculator...")
    
    parser = PDDLParser(SAMPLE_DOMAIN, SAMPLE_PROBLEM)
    calculator = ActionCalculator(parser)
    
    # Get applicable actions
    applicable = calculator.get_applicable_actions(parser.initial_state)
    
    assert len(applicable) > 0, "No applicable actions found"
    print(f"  ✅ Found {len(applicable)} applicable actions")
    
    # Check action structure
    if applicable:
        action = applicable[0]
        assert 'action' in action, "Action missing 'action' field"
        assert 'bindings' in action, "Action missing 'bindings' field"
        assert 'description' in action, "Action missing 'description' field"
        print(f"  ✅ Action structure is correct")
        print(f"     Example: {action['description']}")
    
    return True


def test_game_state():
    """Test game state management"""
    print("\n🎮 Testing Game State...")
    
    parser = PDDLParser(SAMPLE_DOMAIN, SAMPLE_PROBLEM)
    game_state = GameState(parser.initial_state, parser.goal)
    
    # Check initial state
    assert game_state.step_count == 0, "Initial step count should be 0"
    assert len(game_state.current_facts) > 0, "Initial facts should not be empty"
    print(f"  ✅ Initial state has {len(game_state.current_facts)} facts")
    
    # Test goal checking (should not be reached initially)
    goal_reached = game_state.is_goal_reached()
    assert goal_reached == False, "Goal should not be reached initially"
    print("  ✅ Goal correctly not reached at start")
    
    # Test state serialization
    state_dict = game_state.to_dict()
    assert 'facts' in state_dict, "State dict missing 'facts'"
    assert 'step_count' in state_dict, "State dict missing 'step_count'"
    print("  ✅ State serialization works")
    
    return True


def test_game_engine():
    """Test complete game engine"""
    print("\n🎯 Testing Game Engine...")
    
    try:
        engine = GameEngine(SAMPLE_DOMAIN, SAMPLE_PROBLEM)
        print("  ✅ Game engine initialized")
        
        # Initialize game
        game_data = engine.initialize_game()
        assert 'step' in game_data, "Game data missing 'step'"
        assert 'available_actions' in game_data, "Game data missing 'available_actions'"
        print(f"  ✅ Game initialized with {len(game_data['available_actions'])} actions")
        
        # Get available actions
        actions = engine.get_available_actions()
        assert len(actions) > 0, "No available actions"
        print(f"  ✅ {len(actions)} available actions in initial state")
        
        # Try to execute an action
        if actions:
            action = actions[0]
            print(f"  🎬 Attempting action: {action['display_text']}")
            result = engine.execute_action(action['action'], action['bindings'])
            
            assert 'step' in result, "Result missing 'step'"
            assert result['step'] == 1, "Step count should be 1 after first action"
            print(f"  ✅ Action executed successfully, now at step {result['step']}")
            print(f"  📊 {len(result['available_actions'])} actions now available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Game engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_game_flow():
    """Test a complete game play-through"""
    print("\n🎲 Testing Full Game Flow...")
    
    try:
        engine = GameEngine(SAMPLE_DOMAIN, SAMPLE_PROBLEM)
        
        max_steps = 10
        step = 0
        
        while step < max_steps and not engine.is_goal_reached():
            actions = engine.get_available_actions()
            
            if not actions:
                print(f"  ⚠️ No actions available at step {step}")
                break
            
            # Take first available action
            action = actions[0]
            print(f"  Step {step}: {action['display_text']}")
            
            result = engine.execute_action(action['action'], action['bindings'])
            step = result['step']
            
            if result['goal_reached']:
                print(f"  🎉 Goal reached in {step} steps!")
                return True
        
        if not engine.is_goal_reached():
            print(f"  ℹ️ Game not completed in {max_steps} steps (expected for this test)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Full game flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🧪 Running Game Service Tests")
    print("=" * 60)
    
    tests = [
        test_pddl_parser,
        test_state_evaluator,
        test_action_calculator,
        test_game_state,
        test_game_engine,
        test_full_game_flow
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n❌ Test {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✅ All game service tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some game service tests failed")
        sys.exit(1)
