import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Database settings (for future expansion)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///stroka.db'
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Security settings
    WTF_CSRF_ENABLED = True
    
    # Search settings
    SEARCH_RESULTS_PER_PAGE = 20
    SEARCH_MAX_QUERY_LENGTH = 500

    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///stroka.db'
    
    # Upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Supabase configuration
    SUPABASE_URL = 'https://lsfmkniuvqxnexumooos.supabase.co'
    SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzZm1rbml1dnF4bmV4dW1vb29zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjA2NDA3NSwiZXhwIjoyMDY3NjQwMDc1fQ.b4eyMnP05XcE_Uuk9MQgtrp7UdmuOv-sU0SKZP9ZIK0'
    
    # Mistral AI configuration
    MISTRAL_API_KEY = '6trhjxfirpthKPGAwm9jjtgWlfVKOgfa'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 