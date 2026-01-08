"""
Image Processor Module
Handles image enhancement using Real-ESRGAN and custom dimension/PPI settings
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from models.realesrgan_model import RealESRGANModel


class ImageProcessor:
    """
    Handles image enhancement with ESRGAN and custom processing
    """
    
    def __init__(self, config):
        """
        Initialize ImageProcessor
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.esrgan_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Real-ESRGAN model"""
        try:
            self.esrgan_model = RealESRGANModel(self.config)
            print("ImageProcessor: ESRGAN model initialized successfully")
        except Exception as e:
            print(f"ImageProcessor: Error initializing ESRGAN model: {e}")
            self.esrgan_model = None
    
    def enhance_image(self, input_path, output_path, target_width=None, target_height=None,
                     ppi_horizontal=72, ppi_vertical=72, maintain_aspect=True):
        """
        Enhance image with ESRGAN and apply custom settings
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save enhanced image
            target_width (int, optional): Target width in pixels
            target_height (int, optional): Target height in pixels
            ppi_horizontal (int): Horizontal pixels per inch
            ppi_vertical (int): Vertical pixels per inch
            maintain_aspect (bool): Whether to maintain aspect ratio
            
        Returns:
            dict: Result with success status and output info
        """
        try:
            if not self.esrgan_model:
                return {
                    'success': False,
                    'error': 'ESRGAN model not initialized'
                }
            
            # Read original image
            original_img = cv2.imread(str(input_path))
            if original_img is None:
                return {
                    'success': False,
                    'error': f'Failed to read image from {input_path}'
                }
            
            original_height, original_width = original_img.shape[:2]
            
            # Calculate target dimensions if not provided
            if target_width is None:
                target_width = original_width
            if target_height is None:
                target_height = original_height
            
            # Maintain aspect ratio if requested
            if maintain_aspect and target_width and target_height:
                aspect_ratio = original_width / original_height
                target_aspect = target_width / target_height
                
                if abs(aspect_ratio - target_aspect) > 0.01:
                    # Recalculate to maintain aspect ratio
                    if target_width / original_width > target_height / original_height:
                        target_width = int(target_height * aspect_ratio)
                    else:
                        target_height = int(target_width / aspect_ratio)
            
            # Step 1: Upscale with ESRGAN
            print(f"Upscaling image with ESRGAN...")
            upscaled_img = self.esrgan_model.upscale_image(str(input_path))
            
            # Step 2: Resize to target dimensions if different
            upscaled_height, upscaled_width = upscaled_img.shape[:2]
            
            if target_width != upscaled_width or target_height != upscaled_height:
                print(f"Resizing from {upscaled_width}x{upscaled_height} to {target_width}x{target_height}")
                
                # Use high-quality interpolation
                if target_width > upscaled_width or target_height > upscaled_height:
                    # Upscaling - use cubic interpolation
                    interpolation = cv2.INTER_CUBIC
                else:
                    # Downscaling - use area interpolation
                    interpolation = cv2.INTER_AREA
                
                final_img = cv2.resize(
                    upscaled_img,
                    (target_width, target_height),
                    interpolation=interpolation
                )
            else:
                final_img = upscaled_img
            
            # Step 3: Apply PPI settings (save as metadata)
            # Convert to PIL for better metadata handling
            final_img_rgb = cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(final_img_rgb)
            
            # Calculate DPI (dots per inch) from PPI
            # PIL uses DPI for saving
            dpi_horizontal = ppi_horizontal
            dpi_vertical = ppi_vertical
            
            # Determine output format from file extension
            output_ext = Path(output_path).suffix.lower()
            
            # Save with appropriate settings
            if output_ext in ['.png']:
                pil_image.save(
                    str(output_path),
                    'PNG',
                    dpi=(dpi_horizontal, dpi_vertical),
                    optimize=True
                )
            elif output_ext in ['.jpg', '.jpeg']:
                pil_image.save(
                    str(output_path),
                    'JPEG',
                    dpi=(dpi_horizontal, dpi_vertical),
                    quality=95,
                    optimize=True
                )
            elif output_ext == '.bmp':
                pil_image.save(
                    str(output_path),
                    'BMP',
                    dpi=(dpi_horizontal, dpi_vertical)
                )
            elif output_ext in ['.tif', '.tiff']:
                pil_image.save(
                    str(output_path),
                    'TIFF',
                    dpi=(dpi_horizontal, dpi_vertical),
                    compression='tiff_lzw'
                )
            elif output_ext == '.webp':
                pil_image.save(
                    str(output_path),
                    'WEBP',
                    dpi=(dpi_horizontal, dpi_vertical),
                    quality=95
                )
            else:
                # Default to PNG
                pil_image.save(
                    str(output_path),
                    'PNG',
                    dpi=(dpi_horizontal, dpi_vertical)
                )
            
            print(f"Enhanced image saved to {output_path}")
            
            # Calculate physical dimensions in inches
            width_inches = target_width / ppi_horizontal
            height_inches = target_height / ppi_vertical
            
            return {
                'success': True,
                'output_info': {
                    'width': target_width,
                    'height': target_height,
                    'ppi_horizontal': ppi_horizontal,
                    'ppi_vertical': ppi_vertical,
                    'width_inches': round(width_inches, 2),
                    'height_inches': round(height_inches, 2),
                    'file_path': str(output_path),
                    'format': output_ext.replace('.', '').upper()
                }
            }
            
        except Exception as e:
            print(f"Error during image enhancement: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def upscale_only(self, input_path, output_path, scale_factor=None):
        """
        Upscale image using ESRGAN without custom dimensions
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save upscaled image
            scale_factor (int, optional): Scale factor (uses model default if None)
            
        Returns:
            dict: Result with success status and output info
        """
        try:
            if not self.esrgan_model:
                return {
                    'success': False,
                    'error': 'ESRGAN model not initialized'
                }
            
            # Upscale with ESRGAN
            upscaled_img = self.esrgan_model.upscale_image(str(input_path))
            
            # Save
            cv2.imwrite(str(output_path), upscaled_img)
            
            height, width = upscaled_img.shape[:2]
            
            return {
                'success': True,
                'output_info': {
                    'width': width,
                    'height': height,
                    'file_path': str(output_path)
                }
            }
            
        except Exception as e:
            print(f"Error during upscaling: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def resize_image(self, input_path, output_path, width, height, maintain_quality=True):
        """
        Resize image without ESRGAN enhancement
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save resized image
            width (int): Target width
            height (int): Target height
            maintain_quality (bool): Use high-quality interpolation
            
        Returns:
            dict: Result with success status
        """
        try:
            img = cv2.imread(str(input_path))
            if img is None:
                return {
                    'success': False,
                    'error': f'Failed to read image from {input_path}'
                }
            
            # Choose interpolation method
            if maintain_quality:
                interpolation = cv2.INTER_LANCZOS4
            else:
                interpolation = cv2.INTER_LINEAR
            
            resized = cv2.resize(img, (width, height), interpolation=interpolation)
            cv2.imwrite(str(output_path), resized)
            
            return {
                'success': True,
                'output_info': {
                    'width': width,
                    'height': height,
                    'file_path': str(output_path)
                }
            }
            
        except Exception as e:
            print(f"Error during resizing: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_model_info(self):
        """
        Get information about the ESRGAN model
        
        Returns:
            dict: Model information or error
        """
        if self.esrgan_model:
            return self.esrgan_model.get_model_info()
        else:
            return {
                'error': 'ESRGAN model not initialized'
            }
    
    def cleanup(self):
        """Clean up resources"""
        if self.esrgan_model:
            self.esrgan_model.unload_model()