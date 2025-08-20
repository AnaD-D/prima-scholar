"""
Excellence API endpoints
"""

from flask import Blueprint, request, jsonify, current_app
import logging

excellence_bp = Blueprint('excellence', __name__)
logger = logging.getLogger(__name__)

@excellence_bp.route('/excellence-profile/<student_id>', methods=['GET'])
def get_excellence_profile(student_id):
    """Get student excellence profile"""
    try:
        excellence_engine = current_app.excellence_engine
        
        # Calculate current excellence score
        excellence_data = excellence_engine.calculate_excellence_score(student_id)
        
        if 'error' in excellence_data:
            return jsonify(excellence_data), 400
        
        # Get trajectory data
        trajectory_query = """
        SELECT excellence_score, trajectory_date
        FROM excellence_trajectory
        WHERE student_id = :student_id
        ORDER BY trajectory_date ASC
        """
        
        trajectory = current_app.db_manager.execute_query(
            trajectory_query, {'student_id': student_id}
        )
        
        # Format trajectory for charts
        trajectory_data = [
            {
                'date': row['trajectory_date'].strftime('%Y-%m-%d'),
                'excellence_score': float(row['excellence_score'])
            }
            for row in trajectory
        ]
        
        result = {
            **excellence_data,
            'trajectory': trajectory_data,
            'student_id': student_id
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Excellence profile retrieval failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@excellence_bp.route('/update-excellence-profile', methods=['POST'])
def update_excellence_profile():
    """Update student excellence profile"""
    try:
        data = request.json
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'error': 'student_id is required'}), 400
        
        excellence_engine = current_app.excellence_engine
        
        # Recalculate excellence score
        excellence_data = excellence_engine.calculate_excellence_score(student_id)
        
        return jsonify({
            'success': True,
            'updated_profile': excellence_data
        })
        
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        return jsonify({'error': str(e)}), 500