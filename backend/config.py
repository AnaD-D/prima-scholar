"""
Prima Scholar Configuration
Centralized configuration management for all environments
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'prima-scholar-secret-key-change-in-production'
    
    # Database Configuration
    TIDB_CONNECTION_STRING = os.environ.get('TIDB_CONNECTION_STRING')
    TIDB_HOST = os.environ.get('TIDB_HOST', 'localhost')
    TIDB_PORT = int(os.environ.get('TIDB_PORT', 4000))
    TIDB_DATABASE = os.environ.get('TIDB_DATABASE', 'prima_scholar')
    TIDB_USERNAME = os.environ.get('TIDB_USERNAME', 'root')
    TIDB_PASSWORD = os.environ.get('TIDB_PASSWORD', '')
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4')
    OPENAI_EMBEDDING_MODEL = os.environ.get('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    
    # Application Settings
    MAX_UPLOAD_SIZE = os.environ.get('MAX_UPLOAD_SIZE', '50MB')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md', 'doc', 'pptx'}
    
    # External API Configuration
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    GOOGLE_CALENDAR_API_KEY = os.environ.get('GOOGLE_CALENDAR_API_KEY')
    LINKEDIN_API_KEY = os.environ.get('LINKEDIN_API_KEY')
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
    
    # Caching Configuration
    CACHE_TTL = int(os.environ.get('CACHE_TTL', 300))  # 5 minutes
    PREDICTION_CACHE_TTL = int(os.environ.get('PREDICTION_CACHE_TTL', 600))  # 10 minutes
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'True').lower() == 'true'
    
    # Performance Settings
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 4))
    GUNICORN_WORKERS = int(os.environ.get('GUNICORN_WORKERS', 3))
    GUNICORN_THREADS = int(os.environ.get('GUNICORN_THREADS', 2))
    
    # Security Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', './logs/prima_scholar.log')
    ENABLE_FILE_LOGGING = os.environ.get('ENABLE_FILE_LOGGING', 'True').lower() == 'true'
    
    # Excellence Engine Configuration
    EXCELLENCE_THRESHOLDS = {
        'Dean_List': {'gpa_min': 3.5, 'excellence_score_min': 75},
        'Magna_Cum_Laude': {'gpa_min': 3.7, 'excellence_score_min': 85},
        'Summa_Cum_Laude': {'gpa_min': 3.9, 'excellence_score_min': 95},
        'Phi_Beta_Kappa': {'gpa_min': 3.8, 'excellence_score_min': 90},
        'Rhodes_Scholar': {'gpa_min': 3.9, 'excellence_score_min': 98},
        'Fulbright_Scholar': {'gpa_min': 3.8, 'excellence_score_min': 92}
    }
    
    # Academic Level Classifications
    ACADEMIC_LEVELS = {
        'undergraduate': {'weight': 1.0, 'complexity_multiplier': 1.0},
        'graduate': {'weight': 1.2, 'complexity_multiplier': 1.3},
        'doctoral': {'weight': 1.5, 'complexity_multiplier': 1.6},
        'postdoc': {'weight': 1.8, 'complexity_multiplier': 2.0}
    }
    
    # Excellence Tier Keywords
    EXCELLENCE_KEYWORDS = {
        'elite': ['seminal', 'groundbreaking', 'paradigm', 'revolutionary', 'fundamental theorem'],
        'scholar': ['theoretical framework', 'methodology', 'empirical analysis', 'systematic approach'],
        'advanced': ['complex', 'sophisticated', 'comprehensive', 'in-depth analysis'],
        'basic': ['introduction', 'overview', 'basic concepts', 'fundamentals']
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        'predictions': '60 per minute',
        'mentorship': '30 per minute',
        'uploads': '10 per minute',
        'general': '100 per minute'
    }
    
    @staticmethod
    def validate_config():
        """Validate critical configuration values"""
        errors = []
        
        if not Config.TIDB_CONNECTION_STRING:
            errors.append("TIDB_CONNECTION_STRING is required")
            
        if not Config.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
            
        if Config.OPENAI_API_KEY and not Config.OPENAI_API_KEY.startswith('sk-'):
            errors.append("OPENAI_API_KEY format appears invalid")
            
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    DEVELOPMENT_MODE = True
    
    # Relaxed settings for development
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'
    ENABLE_FILE_LOGGING = True
    
    # Mock external APIs in development
    MOCK_EXTERNAL_APIS = os.environ.get('MOCK_EXTERNAL_APIS', 'False').lower() == 'true'
    DEBUG_PREDICTIONS = os.environ.get('DEBUG_PREDICTIONS', 'False').lower() == 'true'

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    DEVELOPMENT_MODE = False
    
    # Strict security settings
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'INFO'
    ENABLE_FILE_LOGGING = True
    
    # Performance optimizations
    CACHE_TTL = 600  # 10 minutes
    PREDICTION_CACHE_TTL = 1800  # 30 minutes

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    
    # Test database
    TIDB_DATABASE = 'prima_scholar_test'
    
    # Disable external services
    MOCK_EXTERNAL_APIS = True
    ENABLE_CACHING = False
    
    # Fast testing
    CACHE_TTL = 0
    PREDICTION_CACHE_TTL = 0

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    config_class = config.get(env, config['default'])
    
    # Validate configuration
    config_class.validate_config()
    
    return config_class