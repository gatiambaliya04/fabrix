"""
Script to manually download Real-ESRGAN model weights
Run this before starting the application
"""

import os
import urllib.request
import ssl
from pathlib import Path

# Model information
MODEL_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
MODEL_NAME = "RealESRGAN_x4plus.pth"

# Create weights directory
weights_dir = Path("models/weights")
weights_dir.mkdir(parents=True, exist_ok=True)

model_path = weights_dir / MODEL_NAME

# Check if model already exists
if model_path.exists():
    print(f"✓ Model already exists at: {model_path}")
    print(f"  File size: {model_path.stat().st_size / (1024*1024):.2f} MB")
    response = input("Do you want to re-download? (y/n): ")
    if response.lower() != 'y':
        print("Skipping download.")
        exit(0)

print(f"Downloading Real-ESRGAN model...")
print(f"URL: {MODEL_URL}")
print(f"Destination: {model_path}")
print("\nThis may take a few minutes (file size: ~64 MB)...\n")

try:
    # Create an SSL context that doesn't verify certificates
    # This is necessary for some systems with certificate issues
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Download with progress
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        print(f"\rProgress: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='')
    
    urllib.request.urlretrieve(
        MODEL_URL,
        str(model_path),
        reporthook=report_progress,
        context=ssl_context
    )
    
    print("\n\n✓ Model downloaded successfully!")
    print(f"  Location: {model_path}")
    print(f"  File size: {model_path.stat().st_size / (1024*1024):.2f} MB")
    print("\nYou can now run the application with: python app.py")
    
except Exception as e:
    print(f"\n\n✗ Error downloading model: {e}")
    print("\n--- Alternative Method ---")
    print("If automatic download fails, manually download from:")
    print(f"  {MODEL_URL}")
    print(f"\nThen save it to:")
    print(f"  {model_path.absolute()}")
    exit(1)