"""
Utils package for image processing
Contains image enhancement, outline extraction, and utility functions
"""

from .image_processor import ImageProcessor
from .outline_extractor import OutlineExtractor
from .image_utils import ImageUtils

__all__ = [
    'ImageProcessor',
    'OutlineExtractor',
    'ImageUtils'
]

__version__ = '1.0.0'
__author__ = 'Image Enhancer Team'