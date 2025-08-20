"""
Prima Scholar - Main Flask Application
AI-powered Academic Excellence Engine
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import application modules
from config import Config
from database.connection import DatabaseManager
from models.excellence_engine import ExcellenceEngine
from services.academic_processor import AcademicProcessor
from services.scholar_mentorship import ScholarMentorshipService
from services.prediction_service import PredictionService
from services.resource_curator import ResourceCurator
from services.external_tools import ExternalToolsService

# Import API routes
from routes.excellence_api import excellence_bp
from routes.mentorship_api import mentorship_bp
from routes.prediction_api import prediction_bp
from routes.resources_api import resources_bp

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'].split(','))
    
    # Setup logging
    setup_logging(app)
    
    # Initialize database
    db_manager = DatabaseManager(app.config['TIDB_CONNECTION_STRING'])
    app.db_manager = db_manager
    
    # Initialize services
    init_services(app)
    
    # Register blueprints
    app.register_blueprint(excellence_bp, url_prefix='/api')
    app.register_blueprint(mentorship_bp, url_prefix='/api')
    app.register_blueprint(prediction_bp, url_prefix='/api')
    app.register_blueprint(resources_bp, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Test database connection
            db_status = app.db_manager.test_connection()
            
            # Test Redis connection
            redis_status = app.prediction_service.test_cache()
            
            return jsonify({
                'status': 'healthy',
                'service': 'prima-scholar-api',
                'version': '1.0.0',
                'database': 'connected' if db_status else 'disconnected',
                'cache': 'connected' if redis_status else 'disconnected'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500
    
    @app.route('/')
    def index():
        """Root endpoint with API information"""
        return jsonify({
            'service': 'Prima Scholar API',
            'version': '1.0.0',
            'description': 'AI-powered Academic Excellence Engine',
            'endpoints': {
                'health': '/health',
                'excellence': '/api/excellence-profile/{student_id}',
                'predictions': '/api/distinction-predictions/{student_id}',
                'mentorship': '/api/scholar-mentorship',
                'resources': '/api/elite-resources/{student_id}',
                'roadmap': '/api/excellence-roadmap/{student_id}'
            },
            'documentation': '/docs'
        })
    
    @app.route('/docs')
    def api_docs():
        """API documentation endpoint"""
        return jsonify({
            'title': 'Prima Scholar API Documentation',
            'version': '1.0.0',
            'description': 'Complete API reference for Prima Scholar Academic Excellence Engine',
            'base_url': request.host_url + 'api',
            'authentication': 'Bearer Token (Optional)',
            'rate_limits': {
                'predictions': '60 requests per minute',
                'mentorship': '30 requests per minute',
                'uploads': '10 requests per minute'
            },
            'endpoints': get_api_endpoints_documentation()
        })
    
    return app

def setup_logging(app):
    """Configure application logging"""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File logging if enabled
    if app.config.get('ENABLE_FILE_LOGGING'):
        log_file = app.config.get('LOG_FILE', 'logs/prima_scholar.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        app.logger.addHandler(file_handler)
    
    app.logger.info('Prima Scholar API starting up...')

def init_services(app):
    """Initialize all application services"""
    try:
        # Initialize Excellence Engine
        app.excellence_engine = ExcellenceEngine(
            app.db_manager,
            app.config['OPENAI_API_KEY']
        )
        
        # Initialize Academic Processor
        app.academic_processor = AcademicProcessor(
            app.config['OPENAI_API_KEY'],
            app.db_manager
        )
        
        # Initialize Scholar Mentorship Service
        app.mentorship_service = ScholarMentorshipService(
            app.config['OPENAI_API_KEY'],
            app.excellence_engine,
            app.db_manager
        )
        
        # Initialize Prediction Service
        app.prediction_service = PredictionService(
            app.excellence_engine,
            app.db_manager,
            app.config.get('REDIS_URL')
        )
        
        # Initialize Resource Curator
        app.resource_curator = ResourceCurator(
            app.db_manager,
            app.config['OPENAI_API_KEY']
        )
        
        # Initialize External Tools Service
        app.external_tools = ExternalToolsService(
            sendgrid_key=app.config.get('SENDGRID_API_KEY'),
            google_calendar_key=app.config.get('GOOGLE_CALENDAR_API_KEY'),
            linkedin_key=app.config.get('LINKEDIN_API_KEY'),
            slack_token=app.config.get('SLACK_BOT_TOKEN')
        )
        
        app.logger.info('All services initialized successfully')
        
    except Exception as e:
        app.logger.error(f'Failed to initialize services: {str(e)}')
        raise

def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Invalid request data'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {str(error)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

def get_api_endpoints_documentation():
    """Return API endpoints documentation"""
    return {
        'excellence_profile': {
            'endpoint': '/excellence-profile/{student_id}',
            'method': 'GET',
            'description': 'Get student excellence profile and current score',
            'parameters': {
                'student_id': 'Unique student identifier'
            },
            'response': {
                'excellence_score': 'Current excellence score (0-100)',
                'target_distinction': 'Target academic distinction',
                'trajectory': 'Historical score progression',
                'factors': 'Excellence contributing factors'
            }
        },
        'distinction_predictions': {
            'endpoint': '/distinction-predictions/{student_id}',
            'method': 'GET',
            'description': 'Get real-time predictions for all academic distinctions',
            'parameters': {
                'student_id': 'Unique student identifier'
            },
            'response': {
                'predictions': 'Probability predictions for each distinction',
                'confidence': 'Prediction confidence levels',
                'factors': 'Key success factors',
                'recommendations': 'Improvement recommendations'
            }
        },
        'scholar_mentorship': {
            'endpoint': '/scholar-mentorship',
            'method': 'POST',
            'description': 'Get scholar-level mentorship response to academic queries',
            'body': {
                'student_id': 'Unique student identifier',
                'query': 'Academic question or topic',
                'context': 'Optional context from uploaded documents'
            },
            'response': {
                'scholar_response': 'Elite academic mentorship response',
                'theoretical_frameworks': 'Relevant academic frameworks',
                'excellence_impact': 'How this elevates academic standing',
                'probability_updates': 'Updated distinction probabilities'
            }
        },
        'excellence_roadmap': {
            'endpoint': '/excellence-roadmap/{student_id}',
            'method': 'GET',
            'description': 'Get personalized roadmap to academic excellence',
            'parameters': {
                'student_id': 'Unique student identifier'
            },
            'response': {
                'immediate_actions': 'Actions for next 30 days',
                'milestone_targets': 'Key milestones and deadlines',
                'resource_recommendations': 'Elite academic resources',
                'networking_opportunities': 'Scholar network connections'
            }
        }
    }

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )