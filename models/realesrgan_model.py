"""
Real-ESRGAN Model Handler
Manages loading and inference of Real-ESRGAN models for image upscaling
"""

import os
import ssl
import torch
import numpy as np
from pathlib import Path
from PIL import Image
import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

# Fix SSL certificate verification issues
ssl._create_default_https_context = ssl._create_unverified_context


class RealESRGANModel:
    """Handler for Real-ESRGAN model operations"""
    
    def __init__(self, config):
        """
        Initialize Real-ESRGAN model
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.model = None
        self.device = None
        self.model_loaded = False
        
        # Set device
        self._setup_device()
        
        # Load model
        self._load_model()
    
    def _setup_device(self):
        """Setup computation device (GPU/CPU)"""
        if self.config['USE_GPU'] and torch.cuda.is_available():
            self.device = torch.device('cuda')
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device('cpu')
            print("Using CPU for inference")
    
    def _load_model(self):
        """Load Real-ESRGAN model with appropriate weights"""
        try:
            model_name = self.config['ESRGAN_MODEL_NAME']
            scale = self.config['ESRGAN_SCALE']
            
            # Define model architecture based on model name
            if model_name == 'RealESRGAN_x4plus':
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32,
                    scale=4
                )
                model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
                
            elif model_name == 'RealESRGAN_x2plus':
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32,
                    scale=2
                )
                model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
                
            elif model_name == 'RealESRGANv2-animevideo-xsx4':
                model = SRVGGNetCompact(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_conv=32,
                    upscale=4,
                    act_type='prelu'
                )
                model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth'
                
            else:
                # Default to x4plus
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32,
                    scale=4
                )
                model_path = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
            
            # Initialize upsampler
            self.model = RealESRGANer(
                scale=scale,
                model_path=model_path,
                model=model,
                tile=0,  # 0 means no tile, process whole image
                tile_pad=10,
                pre_pad=0,
                half=False if self.device == torch.device('cpu') else True,  # Use FP16 on GPU
                device=self.device
            )
            
            self.model_loaded = True
            print(f"Model {model_name} loaded successfully")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model_loaded = False
            raise
    
    def upscale_image(self, image_path, output_path=None):
        """
        Upscale an image using Real-ESRGAN
        
        Args:
            image_path (str): Path to input image
            output_path (str, optional): Path to save output image
            
        Returns:
            numpy.ndarray: Upscaled image array (BGR format)
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Cannot perform upscaling.")
        
        try:
            # Read image
            img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError(f"Failed to read image from {image_path}")
            
            # Perform upscaling
            output, _ = self.model.enhance(img, outscale=self.config['ESRGAN_SCALE'])
            
            # Save if output path provided
            if output_path:
                cv2.imwrite(str(output_path), output)
                print(f"Upscaled image saved to {output_path}")
            
            return output
            
        except Exception as e:
            print(f"Error during upscaling: {e}")
            raise
    
    def upscale_with_custom_scale(self, image_path, output_path, target_width, target_height):
        """
        Upscale image and resize to specific dimensions
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path to save output image
            target_width (int): Target width in pixels
            target_height (int): Target height in pixels
            
        Returns:
            dict: Information about the upscaled image
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Cannot perform upscaling.")
        
        try:
            # First upscale with Real-ESRGAN
            upscaled_img = self.upscale_image(image_path)
            
            # Get current dimensions
            current_height, current_width = upscaled_img.shape[:2]
            
            # If target dimensions differ, resize
            if target_width and target_height:
                if current_width != target_width or current_height != target_height:
                    # Use high-quality interpolation
                    upscaled_img = cv2.resize(
                        upscaled_img,
                        (target_width, target_height),
                        interpolation=cv2.INTER_LANCZOS4
                    )
            
            # Save final image
            cv2.imwrite(str(output_path), upscaled_img)
            
            return {
                'success': True,
                'width': upscaled_img.shape[1],
                'height': upscaled_img.shape[0],
                'channels': upscaled_img.shape[2] if len(upscaled_img.shape) > 2 else 1
            }
            
        except Exception as e:
            print(f"Error during custom scale upscaling: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_model_info(self):
        """
        Get information about the loaded model
        
        Returns:
            dict: Model information
        """
        return {
            'model_name': self.config['ESRGAN_MODEL_NAME'],
            'scale': self.config['ESRGAN_SCALE'],
            'device': str(self.device),
            'loaded': self.model_loaded,
            'gpu_available': torch.cuda.is_available(),
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
    
    def unload_model(self):
        """Unload model from memory"""
        if self.model:
            del self.model
            self.model = None
            self.model_loaded = False
            
            # Clear GPU cache if using CUDA
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print("Model unloaded from memory")
    
    def reload_model(self):
        """Reload the model"""
        self.unload_model()
        self._load_model()