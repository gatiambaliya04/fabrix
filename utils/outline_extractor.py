"""
Outline Extractor Module
Handles precise outline extraction using advanced edge detection algorithms
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path


class OutlineExtractor:
    """
    Handles outline extraction from images using Canny edge detection
    and other advanced techniques
    """
    
    def __init__(self, config):
        """
        Initialize OutlineExtractor
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.default_thickness = config.get('OUTLINE_THICKNESS', 1)
        self.canny_threshold1 = config.get('CANNY_THRESHOLD1', 50)
        self.canny_threshold2 = config.get('CANNY_THRESHOLD2', 150)
    
    def extract_outline(self, input_path, output_path, thickness=None):
        """
        Extract outline from image using advanced edge detection
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save outlined image
            thickness (int, optional): Line thickness in pixels (1-5)
            
        Returns:
            dict: Result with success status and output info
        """
        try:
            # Use default thickness if not provided
            if thickness is None:
                thickness = self.default_thickness
            
            # Validate thickness
            thickness = max(1, min(5, thickness))
            
            # Read image
            img = cv2.imread(str(input_path))
            if img is None:
                return {
                    'success': False,
                    'error': f'Failed to read image from {input_path}'
                }
            
            print(f"Processing image: {img.shape}")
            
            # Step 1: Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Step 2: Apply Gaussian blur to reduce noise
            # Larger kernel for better noise reduction
            blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
            
            # Step 3: Apply Canny edge detection
            edges = cv2.Canny(
                blurred,
                self.canny_threshold1,
                self.canny_threshold2,
                apertureSize=3,
                L2gradient=True
            )
            
            # Step 4: Apply morphological operations to connect edges
            # This helps create more continuous lines
            if thickness > 1:
                kernel = cv2.getStructuringElement(
                    cv2.MORPH_ELLIPSE,
                    (thickness, thickness)
                )
                edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Step 5: Invert the image (we want black lines on white background)
            outline = cv2.bitwise_not(edges)
            
            # Step 6: Ensure pure white background and black lines
            # This removes any gray artifacts
            _, outline = cv2.threshold(outline, 127, 255, cv2.THRESH_BINARY)
            
            # Get output format from file extension
            output_ext = Path(output_path).suffix.lower()
            
            # Save the outline
            if output_ext in ['.png']:
                cv2.imwrite(str(output_path), outline, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            elif output_ext in ['.jpg', '.jpeg']:
                cv2.imwrite(str(output_path), outline, [cv2.IMWRITE_JPEG_QUALITY, 95])
            elif output_ext == '.bmp':
                cv2.imwrite(str(output_path), outline)
            elif output_ext in ['.tif', '.tiff']:
                cv2.imwrite(str(output_path), outline)
            elif output_ext == '.webp':
                cv2.imwrite(str(output_path), outline, [cv2.IMWRITE_WEBP_QUALITY, 95])
            else:
                # Default to PNG
                cv2.imwrite(str(output_path), outline, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            
            print(f"Outline extracted and saved to {output_path}")
            
            height, width = outline.shape[:2]
            
            return {
                'success': True,
                'output_info': {
                    'width': width,
                    'height': height,
                    'thickness': thickness,
                    'file_path': str(output_path),
                    'format': output_ext.replace('.', '').upper()
                }
            }
            
        except Exception as e:
            print(f"Error during outline extraction: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_outline_advanced(self, input_path, output_path, thickness=None,
                                 auto_threshold=True):
        """
        Advanced outline extraction with adaptive thresholding
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save outlined image
            thickness (int, optional): Line thickness in pixels
            auto_threshold (bool): Use automatic threshold detection
            
        Returns:
            dict: Result with success status and output info
        """
        try:
            if thickness is None:
                thickness = self.default_thickness
            
            thickness = max(1, min(5, thickness))
            
            # Read image
            img = cv2.imread(str(input_path))
            if img is None:
                return {
                    'success': False,
                    'error': f'Failed to read image from {input_path}'
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to preserve edges while reducing noise
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Calculate optimal thresholds if auto_threshold is enabled
            if auto_threshold:
                # Use Otsu's method to find optimal threshold
                _, binary = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                threshold1 = int(np.median(binary) * 0.33)
                threshold2 = int(np.median(binary) * 0.66)
            else:
                threshold1 = self.canny_threshold1
                threshold2 = self.canny_threshold2
            
            # Apply Canny edge detection
            edges = cv2.Canny(filtered, threshold1, threshold2, L2gradient=True)
            
            # Apply morphological closing to connect nearby edges
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Adjust thickness if needed
            if thickness > 1:
                thick_kernel = cv2.getStructuringElement(
                    cv2.MORPH_ELLIPSE,
                    (thickness, thickness)
                )
                closed = cv2.dilate(closed, thick_kernel, iterations=1)
            
            # Invert for black lines on white background
            outline = cv2.bitwise_not(closed)
            
            # Ensure pure binary image
            _, outline = cv2.threshold(outline, 127, 255, cv2.THRESH_BINARY)
            
            # Save
            output_ext = Path(output_path).suffix.lower()
            if output_ext in ['.png']:
                cv2.imwrite(str(output_path), outline, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            else:
                cv2.imwrite(str(output_path), outline)
            
            height, width = outline.shape[:2]
            
            return {
                'success': True,
                'output_info': {
                    'width': width,
                    'height': height,
                    'thickness': thickness,
                    'file_path': str(output_path),
                    'format': output_ext.replace('.', '').upper(),
                    'auto_threshold': auto_threshold
                }
            }
            
        except Exception as e:
            print(f"Error during advanced outline extraction: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_outline_with_detail(self, input_path, output_path, thickness=None,
                                    detail_level='medium'):
        """
        Extract outline with different detail levels
        
        Args:
            input_path (str): Path to input image
            output_path (str): Path to save outlined image
            thickness (int, optional): Line thickness in pixels
            detail_level (str): 'low', 'medium', or 'high'
            
        Returns:
            dict: Result with success status and output info
        """
        try:
            if thickness is None:
                thickness = self.default_thickness
            
            thickness = max(1, min(5, thickness))
            
            # Read image
            img = cv2.imread(str(input_path))
            if img is None:
                return {
                    'success': False,
                    'error': f'Failed to read image from {input_path}'
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Set parameters based on detail level
            if detail_level == 'low':
                blur_kernel = (7, 7)
                threshold1 = 100
                threshold2 = 200
            elif detail_level == 'high':
                blur_kernel = (3, 3)
                threshold1 = 30
                threshold2 = 100
            else:  # medium
                blur_kernel = (5, 5)
                threshold1 = self.canny_threshold1
                threshold2 = self.canny_threshold2
            
            # Apply blur
            blurred = cv2.GaussianBlur(gray, blur_kernel, 1.4)
            
            # Edge detection
            edges = cv2.Canny(blurred, threshold1, threshold2, L2gradient=True)
            
            # Apply thickness
            if thickness > 1:
                kernel = cv2.getStructuringElement(
                    cv2.MORPH_ELLIPSE,
                    (thickness, thickness)
                )
                edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Invert
            outline = cv2.bitwise_not(edges)
            
            # Threshold
            _, outline = cv2.threshold(outline, 127, 255, cv2.THRESH_BINARY)
            
            # Save
            cv2.imwrite(str(output_path), outline)
            
            height, width = outline.shape[:2]
            
            return {
                'success': True,
                'output_info': {
                    'width': width,
                    'height': height,
                    'thickness': thickness,
                    'detail_level': detail_level,
                    'file_path': str(output_path)
                }
            }
            
        except Exception as e:
            print(f"Error during detail-level outline extraction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def preview_outline(self, input_path):
        """
        Generate a preview of the outline without saving
        
        Args:
            input_path (str): Path to input image
            
        Returns:
            numpy.ndarray: Outline image array or None if error
        """
        try:
            img = cv2.imread(str(input_path))
            if img is None:
                return None
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
            edges = cv2.Canny(blurred, self.canny_threshold1, self.canny_threshold2)
            outline = cv2.bitwise_not(edges)
            
            return outline
            
        except Exception as e:
            print(f"Error generating preview: {e}")
            return None