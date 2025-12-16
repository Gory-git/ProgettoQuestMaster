"""
Basic tests for QuestMaster backend
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app import create_app
        from app.models import Story, RefinementHistory, GameSession
        from app.services import (
            PDDLGenerationService, 
            PDDLValidationService,
            ReflectionAgentService,
            NarrativeService
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created"""
    try:
        from app import create_app
        app = create_app()
        assert app is not None
        print("✅ Flask app creation successful")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_database_models():
    """Test that database models are properly defined"""
    try:
        from app.models import Story, RefinementHistory, GameSession
        
        # Check Story model has required attributes
        assert hasattr(Story, 'title')
        assert hasattr(Story, 'lore_content')
        assert hasattr(Story, 'pddl_domain')
        assert hasattr(Story, 'pddl_problem')
        
        print("✅ Database models properly defined")
        return True
    except Exception as e:
        print(f"❌ Model check failed: {e}")
        return False

def test_routes():
    """Test that routes are registered"""
    try:
        from app import create_app
        app = create_app()
        
        # Get all registered routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Check key endpoints exist
        assert any('/health' in route for route in routes), "Health route missing"
        assert any('/stories' in route for route in routes), "Stories routes missing"
        assert any('/game/sessions' in route for route in routes), "Game routes missing"
        
        print("✅ Routes properly registered")
        print(f"   Total routes: {len(routes)}")
        return True
    except Exception as e:
        print(f"❌ Route check failed: {e}")
        return False

if __name__ == '__main__':
    print("\n🧪 Running QuestMaster Backend Tests\n")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_creation,
        test_database_models,
        test_routes
    ]
    
    results = []
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        results.append(test())
    
    print("\n" + "=" * 50)
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
