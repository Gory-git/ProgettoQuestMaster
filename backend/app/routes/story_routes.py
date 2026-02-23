"""
Story routes - Phase 1: Story Generation endpoints
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models import Story, RefinementHistory
from app.services import PDDLGenerationService, PDDLValidationService, ReflectionAgentService
import json

bp = Blueprint('story', __name__)

# Initialize services
pddl_service = PDDLGenerationService()
validation_service = PDDLValidationService()
reflection_service = ReflectionAgentService()


@bp.route('/stories', methods=['GET'])
def list_stories():
    """Get all stories"""
    stories = Story.query.all()
    return jsonify({
        'stories': [story.to_dict() for story in stories]
    }), 200


@bp.route('/stories/<int:story_id>', methods=['GET'])
def get_story(story_id):
    """Get a specific story"""
    story = Story.query.get_or_404(story_id)
    return jsonify(story.to_dict()), 200


@bp.route('/stories', methods=['POST'])
def create_story():
    """Create a new story with lore"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    if not data.get('lore_content'):
        return jsonify({'error': 'Lore content is required'}), 400
    
    # Create story
    story = Story(
        title=data['title'],
        description=data.get('description', ''),
        lore_content=data['lore_content'],
        branching_factor_min=data.get('branching_factor_min', 2),
        branching_factor_max=data.get('branching_factor_max', 4),
        depth_min=data.get('depth_min', 3),
        depth_max=data.get('depth_max', 10)
    )
    
    db.session.add(story)
    db.session.commit()
    
    return jsonify(story.to_dict()), 201


@bp.route('/stories/<int:story_id>/generate-pddl', methods=['POST'])
def generate_pddl(story_id):
    """Generate PDDL for a story"""
    story = Story.query.get_or_404(story_id)
    
    try:
        # Generate PDDL
        domain, problem = pddl_service.generate_pddl(
            story.lore_content,
            story.branching_factor_min,
            story.branching_factor_max,
            story.depth_min,
            story.depth_max
        )
        
        # Update story
        story.pddl_domain = domain
        story.pddl_problem = problem
        story.status = 'generated'
        db.session.commit()
        
        return jsonify({
            'message': 'PDDL generated successfully',
            'story': story.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stories/<int:story_id>/validate', methods=['POST'])
def validate_pddl(story_id):
    """Validate PDDL for a story"""
    story = Story.query.get_or_404(story_id)
    
    if not story.pddl_domain or not story.pddl_problem:
        return jsonify({'error': 'No PDDL to validate'}), 400
    
    try:
        # Validate
        is_valid, errors = validation_service.validate(
            story.pddl_domain,
            story.pddl_problem
        )
        
        if is_valid:
            story.is_validated = True
            story.status = 'validated'
            db.session.commit()

            # Report plan existence (uses Fast Downward if available, else trusts BFS inside validate())
            plan_exists, plan_message = validation_service.check_plan_exists(
                story.pddl_domain,
                story.pddl_problem
            )
            
            return jsonify({
                'valid': True,
                'message': 'PDDL is valid',
                'plan_exists': plan_exists,
                'plan_message': plan_message,
                'story': story.to_dict()
            }), 200
        else:
            # Get reflection feedback
            analysis = reflection_service.analyze_errors(
                story.pddl_domain,
                story.pddl_problem,
                errors
            )
            
            # Save to refinement history
            refinement = RefinementHistory(
                story_id=story.id,
                iteration=len(story.refinement_history) + 1,
                pddl_version=story.pddl_domain + '\n\n' + story.pddl_problem,
                validation_errors=json.dumps(errors),
                reflection_feedback=analysis['analysis']
            )
            db.session.add(refinement)
            db.session.commit()
            
            return jsonify({
                'valid': False,
                'errors': errors,
                'reflection': analysis,
                'refinement_id': refinement.id
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stories/<int:story_id>/refine', methods=['POST'])
def refine_pddl(story_id):
    """Refine PDDL based on feedback"""
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    
    author_input = data.get('author_input', '')
    refinement_id = data.get('refinement_id')
    
    if not refinement_id:
        return jsonify({'error': 'Refinement ID required'}), 400
    
    refinement = RefinementHistory.query.get_or_404(refinement_id)
    
    try:
        # Refine domain
        refined_domain = pddl_service.refine_pddl(
            story.pddl_domain,
            json.dumps(json.loads(refinement.validation_errors)),
            refinement.reflection_feedback,
            author_input
        )
        
        # Refine problem
        refined_problem = pddl_service.refine_pddl(
            story.pddl_problem,
            json.dumps(json.loads(refinement.validation_errors)),
            refinement.reflection_feedback,
            author_input
        )
        
        # Update story
        story.pddl_domain = refined_domain
        story.pddl_problem = refined_problem
        
        # Update refinement history
        refinement.author_response = author_input
        
        db.session.commit()
        
        return jsonify({
            'message': 'PDDL refined successfully',
            'story': story.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stories/<int:story_id>/chat', methods=['POST'])
def chat_with_reflection(story_id):
    """Interactive chat with reflection agent"""
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    
    conversation_history = data.get('conversation_history', [])
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        # Get response from reflection agent
        response = reflection_service.generate_chat_response(
            conversation_history,
            user_message
        )
        
        return jsonify({
            'response': response
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stories/<int:story_id>/refinement-history', methods=['GET'])
def get_refinement_history(story_id):
    """Get refinement history for a story"""
    story = Story.query.get_or_404(story_id)
    
    return jsonify({
        'history': [r.to_dict() for r in story.refinement_history]
    }), 200


@bp.route('/stories/<int:story_id>', methods=['PUT'])
def update_story(story_id):
    """Update story details"""
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        story.title = data['title']
    if 'description' in data:
        story.description = data['description']
    if 'lore_content' in data:
        story.lore_content = data['lore_content']
    if 'status' in data:
        story.status = data['status']
    
    db.session.commit()
    
    return jsonify(story.to_dict()), 200


@bp.route('/stories/<int:story_id>', methods=['DELETE'])
def delete_story(story_id):
    """Delete a story"""
    story = Story.query.get_or_404(story_id)
    
    db.session.delete(story)
    db.session.commit()
    
    return jsonify({'message': 'Story deleted'}), 200
