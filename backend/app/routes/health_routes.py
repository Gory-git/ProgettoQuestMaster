"""
Health check routes
"""

from flask import Blueprint, jsonify
import os

bp = Blueprint('health', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'QuestMaster API',
        'version': '1.0.0'
    }), 200


@bp.route('/config', methods=['GET'])
def get_config():
    """Get public configuration (for debugging)"""
    return jsonify({
        'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
        'dalle_enabled': os.getenv('DALLE_ENABLED', 'False').lower() == 'true',
        'fast_downward_available': bool(os.getenv('FAST_DOWNWARD_PATH')),
        'database': 'configured'
    }), 200
