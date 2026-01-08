"""
Image Utilities Module
Helper functions for image processing, validation, and information extraction
"""

import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path


class ImageUtils:
    """
    Utility functions for image processing and management
    """
    
    def __init__(self, config):
        """
        Initialize ImageUtils
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.allowed_extensions = config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'})
    
    def get_image_info(self, image_path):
        """
        Get detailed information about an image
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            dict: Image information including dimensions, format, size, etc.
        """
        try:
            # Get file size
            file_size = os.path.getsize(image_path)
            
            # Open with PIL for metadata
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode
                
                # Get DPI if available
                dpi = img.info.get('dpi', (72, 72))
                if isinstance(dpi, (int, float)):
                    dpi = (dpi, dpi)
                
                # Calculate megapixels
                megapixels = (width * height) / 1_000_000
            
            return {
                'width': width,
                'height': height,
                'format': format_name,
                'mode': mode,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'dpi_horizontal': dpi[0],
                'dpi_vertical': dpi[1],
                'megapixels': round(megapixels, 2),
                'aspect_ratio': round(width / height, 3) if height > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting image info: {e}")
            return {
                'error': str(e)
            }
    
    def validate_image(self, image_path):
        """
        Validate if file is a valid image
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            dict: Validation result with success status and error if any
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'valid': False,
                    'error': 'File does not exist'
                }
            
            # Check file extension
            ext = Path(image_path).suffix.lower().replace('.', '')
            if ext not in self.allowed_extensions:
                return {
                    'valid': False,
                    'error': f'File type .{ext} not allowed'
                }
            
            # Try to open with PIL
            try:
                with Image.open(image_path) as img:
                    img.verify()
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Invalid image file: {str(e)}'
                }
            
            # Check file size
            file_size = os.path.getsize(image_path)
            max_size = self.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
            if file_size > max_size:
                return {
                    'valid': False,
                    'error': f'File too large. Max size: {max_size / (1024 * 1024)}MB'
                }
            
            return {
                'valid': True
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def calculate_new_dimensions(self, original_width, original_height, target_width=None,
                                 target_height=None, maintain_aspect=True):
        """
        Calculate new dimensions with optional aspect ratio lock
        
        Args:
            original_width (int): Original width
            original_height (int): Original height
            target_width (int, optional): Desired width
            target_height (int, optional): Desired height
            maintain_aspect (bool): Maintain aspect ratio
            
        Returns:
            dict: New width and height
        """
        if not maintain_aspect:
            return {
                'width': target_width or original_width,
                'height': target_height or original_height
            }
        
        aspect_ratio = original_width / original_height
        
        if target_width and not target_height:
            # Calculate height based on width
            return {
                'width': target_width,
                'height': int(target_width / aspect_ratio)
            }
        elif target_height and not target_width:
            # Calculate width based on height
            return {
                'width': int(target_height * aspect_ratio),
                'height': target_height
            }
        elif target_width and target_height:
            # Both provided - adjust to maintain aspect ratio
            target_aspect = target_width / target_height
            
            if abs(aspect_ratio - target_aspect) < 0.01:
                # Aspect ratios match
                return {
                    'width': target_width,
                    'height': target_height
                }
            else:
                # Adjust to maintain original aspect ratio
                if target_width / original_width > target_height / original_height:
                    # Height is limiting factor
                    return {
                        'width': int(target_height * aspect_ratio),
                        'height': target_height
                    }
                else:
                    # Width is limiting factor
                    return {
                        'width': target_width,
                        'height': int(target_width / aspect_ratio)
                    }
        else:
            # No target dimensions
            return {
                'width': original_width,
                'height': original_height
            }
    
    def pixels_to_inches(self, pixels, ppi):
        """
        Convert pixels to inches
        
        Args:
            pixels (int): Number of pixels
            ppi (int): Pixels per inch
            
        Returns:
            float: Dimension in inches
        """
        return round(pixels / ppi, 2) if ppi > 0 else 0
    
    def inches_to_pixels(self, inches, ppi):
        """
        Convert inches to pixels
        
        Args:
            inches (float): Dimension in inches
            ppi (int): Pixels per inch
            
        Returns:
            int: Number of pixels
        """
        return int(inches * ppi)
    
    def convert_image_format(self, input_path, output_path, output_format, quality=95):
        """
        Convert image to different format
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save converted image
            output_format (str): Target format (png, jpg, etc.)
            quality (int): Quality for lossy formats (1-100)
            
        Returns:
            dict: Result with success status
        """
        try:
            with Image.open(input_path) as img:
                # Convert RGBA to RGB for formats that don't support transparency
                if img.mode == 'RGBA' and output_format.lower() in ['jpg', 'jpeg', 'bmp']:
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = background
                
                # Save with format-specific options
                if output_format.lower() in ['jpg', 'jpeg']:
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                elif output_format.lower() == 'png':
                    img.save(output_path, 'PNG', optimize=True)
                elif output_format.lower() == 'webp':
                    img.save(output_path, 'WEBP', quality=quality)
                elif output_format.lower() in ['tif', 'tiff']:
                    img.save(output_path, 'TIFF')
                elif output_format.lower() == 'bmp':
                    img.save(output_path, 'BMP')
                else:
                    img.save(output_path)
            
            return {
                'success': True,
                'output_path': output_path
            }
            
        except Exception as e:
            print(f"Error converting image format: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def compare_images(self, image1_path, image2_path):
        """
        Compare two images and calculate similarity
        
        Args:
            image1_path (str): Path to first image
            image2_path (str): Path to second image
            
        Returns:
            dict: Comparison results
        """
        try:
            img1 = cv2.imread(str(image1_path))
            img2 = cv2.imread(str(image2_path))
            
            if img1 is None or img2 is None:
                return {
                    'error': 'Failed to read one or both images'
                }
            
            # Resize images to same size for comparison
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Calculate MSE (Mean Squared Error)
            mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
            
            # Calculate PSNR (Peak Signal-to-Noise Ratio)
            if mse == 0:
                psnr = float('inf')
            else:
                max_pixel = 255.0
                psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            
            # Calculate SSIM-like similarity (simplified)
            similarity = 1 - (mse / (255 ** 2))
            
            return {
                'mse': round(mse, 2),
                'psnr': round(psnr, 2) if psnr != float('inf') else 'Perfect',
                'similarity': round(similarity * 100, 2)  # Percentage
            }
            
        except Exception as e:
            print(f"Error comparing images: {e}")
            return {
                'error': str(e)
            }
    
    def get_dominant_colors(self, image_path, num_colors=5):
        """
        Get dominant colors from an image
        
        Args:
            image_path (str): Path to image
            num_colors (int): Number of dominant colors to extract
            
        Returns:
            list: List of RGB tuples
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return []
            
            # Convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Reshape to list of pixels
            pixels = img.reshape(-1, 3)
            
            # Use KMeans clustering to find dominant colors
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get the colors
            colors = kmeans.cluster_centers_.astype(int)
            
            return [tuple(color) for color in colors]
            
        except ImportError:
            print("sklearn not installed, cannot extract dominant colors")
            return []
        except Exception as e:
            print(f"Error extracting dominant colors: {e}")
            return []
    
    def create_thumbnail(self, input_path, output_path, max_size=(200, 200)):
        """
        Create a thumbnail of an image
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save thumbnail
            max_size (tuple): Maximum dimensions (width, height)
            
        Returns:
            dict: Result with success status
        """
        try:
            with Image.open(input_path) as img:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(output_path)
            
            return {
                'success': True,
                'output_path': output_path
            }
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def estimate_processing_time(self, image_path, operation='enhance'):
        """
        Estimate processing time for an operation
        
        Args:
            image_path (str): Path to image
            operation (str): Type of operation ('enhance' or 'outline')
            
        Returns:
            dict: Estimated time in seconds
        """
        try:
            info = self.get_image_info(image_path)
            
            if 'error' in info:
                return {'error': info['error']}
            
            megapixels = info['megapixels']
            
            # Rough estimates based on operation
            if operation == 'enhance':
                # ESRGAN is more intensive
                base_time = 2  # seconds per megapixel
                estimated = megapixels * base_time
            else:  # outline
                # Edge detection is faster
                base_time = 0.5
                estimated = megapixels * base_time
            
            return {
                'estimated_seconds': round(estimated, 1),
                'estimated_minutes': round(estimated / 60, 1)
            }
            
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def cleanup_old_files(self, directory, max_age_hours=24):
        """
        Remove files older than specified age
        
        Args:
            directory (Path or str): Directory to clean
            max_age_hours (int): Maximum age in hours
            
        Returns:
            dict: Number of files removed
        """
        try:
            import time
            from datetime import datetime, timedelta
            
            directory = Path(directory)
            if not directory.exists():
                return {'removed': 0}
            
            cutoff_time = time.time() - (max_age_hours * 3600)
            removed_count = 0
            
            for file_path in directory.iterdir():
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            removed_count += 1
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
            
            return {
                'removed': removed_count
            }
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return {
                'removed': 0,
                'error': str(e)
            }