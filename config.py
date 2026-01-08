import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Flask Configuration
class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
    
    # Folder paths
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    ENHANCED_FOLDER = BASE_DIR / 'static' / 'enhanced'
    OUTLINED_FOLDER = BASE_DIR / 'static' / 'outlined'
    MODEL_WEIGHTS_FOLDER = BASE_DIR / 'models' / 'weights'
    
    # Create folders if they don't exist
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    ENHANCED_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTLINED_FOLDER.mkdir(parents=True, exist_ok=True)
    MODEL_WEIGHTS_FOLDER.mkdir(parents=True, exist_ok=True)
    
    # Image processing settings
    DEFAULT_PPI = 72  # Default pixels per inch
    MIN_PPI = 1
    MAX_PPI = 1200
    
    # ESRGAN Model settings
    ESRGAN_MODEL_NAME = 'RealESRGAN_x4plus'  # Options: RealESRGAN_x4plus, RealESRGAN_x2plus
    ESRGAN_SCALE = 4  # Upscaling factor (2 or 4)
    USE_GPU = True  # Set to False if no GPU available
    
    # Outline extraction settings
    OUTLINE_THICKNESS = 1  # Pencil-like finish (1-3 pixels)
    CANNY_THRESHOLD1 = 50  # Lower threshold for Canny edge detection
    CANNY_THRESHOLD2 = 150  # Upper threshold for Canny edge detection
    
    # Preview settings
    PREVIEW_MAX_DIMENSION = 1920  # Max dimension for web preview (to avoid memory issues)
    
    # File cleanup settings
    AUTO_CLEANUP = True  # Automatically delete old files
    CLEANUP_AFTER_HOURS = 24  # Delete files older than this many hours
    
    # Download format settings
    SUPPORTED_DOWNLOAD_FORMATS = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp']
    DEFAULT_DOWNLOAD_FORMAT = 'png'
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # In production, make sure to set SECRET_KEY via environment variable
    

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env='default'):
    """Get configuration based on environment"""
    return config.get(env, config['default'])