#!/usr/bin/env python3
"""
Manual test script for game engine without requiring OpenAI
Tests the complete flow from story to gameplay
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set minimal environment
os.environ['DATABASE_URL'] = 'sqlite:///manual_test.db'
os.environ['FLASK_ENV'] = 'testing'
os.environ['OPENAI_API_KEY'] = 'test-key'  # Will use fallback narratives

from app import create_app, db
from app.models import Story, GameSession
from app.services.game_service import GameEngine
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


def print_separator(title=""):
    """Print a nice separator"""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def print_state(engine):
    """Print current game state"""
    print("\n📊 Current State:")
    for fact in sorted(engine.game_state.current_facts):
        print(f"   • {fact}")


def print_actions(actions):
    """Print available actions"""
    print(f"\n🎯 Available Actions ({len(actions)}):")
    for i, action in enumerate(actions, 1):
        print(f"   {i}. {action['display_text']}")
        print(f"      → {action['description']}")


def play_game_interactively():
    """Play a game interactively in the terminal"""
    print_separator("🎮 Interactive Game Test")
    
    # Create game engine
    print("\n🔧 Initializing game engine...")
    engine = GameEngine(SAMPLE_DOMAIN, SAMPLE_PROBLEM)
    print("✅ Engine initialized successfully!")
    
    # Show initial state
    print_state(engine)
    
    # Get goal
    print(f"\n🎯 Goal: {engine.parser.goal['positive']}")
    
    # Game loop
    step = 0
    max_steps = 20
    
    while step < max_steps and not engine.is_goal_reached():
        print_separator(f"Step {step}")
        
        # Get available actions
        actions = engine.get_available_actions()
        
        if not actions:
            print("\n⚠️ No actions available! Game stuck.")
            break
        
        print_actions(actions)
        
        # Get user input
        print("\n❓ Choose an action (enter number):")
        try:
            choice = input("   > ").strip()
            choice_idx = int(choice) - 1
            
            if choice_idx < 0 or choice_idx >= len(actions):
                print("❌ Invalid choice!")
                continue
            
            action = actions[choice_idx]
            
            # Execute action
            print(f"\n⚡ Executing: {action['display_text']}")
            result = engine.execute_action(action['action'], action['bindings'])
            
            step = result['step']
            print(f"✅ Action completed!")
            
            # Show new state
            print_state(engine)
            
            # Check goal
            if result['goal_reached']:
                print_separator("🎉 VICTORY!")
                print(f"\n   You completed the quest in {step} steps!")
                print(f"   Final state has {len(engine.game_state.current_facts)} facts")
                return True
            
        except KeyboardInterrupt:
            print("\n\n👋 Game interrupted by user")
            return False
        except (ValueError, IndexError) as e:
            print(f"❌ Invalid input: {e}")
            continue
    
    if step >= max_steps:
        print_separator("⏱️ Time's Up!")
        print(f"\n   Maximum steps ({max_steps}) reached without completing goal")
    
    return False


def play_game_automated():
    """Play a game automatically to completion"""
    print_separator("🤖 Automated Game Test")
    
    # Create game engine
    print("\n🔧 Initializing game engine...")
    engine = GameEngine(SAMPLE_DOMAIN, SAMPLE_PROBLEM)
    print("✅ Engine initialized successfully!")
    
    # Show initial state
    print_state(engine)
    print(f"\n🎯 Goal: {engine.parser.goal['positive']}")
    
    # Game loop with smart choices
    step = 0
    max_steps = 10
    action_history = []
    
    while step < max_steps and not engine.is_goal_reached():
        print_separator(f"Step {step}")
        
        # Get available actions
        actions = engine.get_available_actions()
        
        if not actions:
            print("\n⚠️ No actions available! Game stuck.")
            break
        
        print_actions(actions)
        
        # Smart choice: prefer pickup actions
        chosen_action = None
        for action in actions:
            if action['action'] == 'pickup':
                chosen_action = action
                break
        
        # Then prefer unlock
        if not chosen_action:
            for action in actions:
                if action['action'] == 'unlock':
                    chosen_action = action
                    break
        
        # Otherwise take first action
        if not chosen_action:
            chosen_action = actions[0]
        
        # Execute action
        print(f"\n⚡ Executing: {chosen_action['display_text']}")
        result = engine.execute_action(chosen_action['action'], chosen_action['bindings'])
        
        action_history.append(chosen_action['display_text'])
        step = result['step']
        print(f"✅ Action completed!")
        
        # Show new state
        print_state(engine)
        
        # Check goal
        if result['goal_reached']:
            print_separator("🎉 VICTORY!")
            print(f"\n   Quest completed in {step} steps!")
            print(f"\n   Action sequence:")
            for i, action in enumerate(action_history, 1):
                print(f"      {i}. {action}")
            return True
    
    if step >= max_steps:
        print_separator("⏱️ Time's Up!")
        print(f"\n   Maximum steps ({max_steps}) reached without completing goal")
    
    return False


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("  🎮 QuestMaster Game Engine Manual Test")
    print("=" * 70)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        # Interactive mode
        success = play_game_interactively()
    else:
        # Automated mode (default)
        success = play_game_automated()
    
    print("\n" + "=" * 70)
    if success:
        print("  ✅ Game completed successfully!")
    else:
        print("  ℹ️ Game ended without reaching goal")
    print("=" * 70 + "\n")
    
    sys.exit(0 if success else 1)
