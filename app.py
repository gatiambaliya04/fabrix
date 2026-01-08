import os
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json

from config import get_config
from utils.image_processor import ImageProcessor
from utils.outline_extractor import OutlineExtractor
from utils.image_utils import ImageUtils

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(get_config(env))

# Initialize processors
image_processor = ImageProcessor(app.config)
outline_extractor = OutlineExtractor(app.config)
image_utils = ImageUtils(app.config)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def cleanup_old_files():
    """Remove files older than specified hours"""
    if not app.config['AUTO_CLEANUP']:
        return
    
    cutoff_time = datetime.now() - timedelta(hours=app.config['CLEANUP_AFTER_HOURS'])
    folders = [app.config['UPLOAD_FOLDER'], app.config['ENHANCED_FOLDER'], app.config['OUTLINED_FOLDER']]
    
    for folder in folders:
        for file_path in folder.glob('*'):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    try:
                        file_path.unlink()
                    except Exception as e:
                        app.logger.error(f"Error deleting {file_path}: {e}")


@app.route('/')
def index():
    """Landing page"""
    cleanup_old_files()
    return render_template('index.html')


@app.route('/enhancer')
def enhancer():
    """Image enhancement page"""
    return render_template('enhancer.html')


@app.route('/outliner')
def outliner():
    """Outline extraction page"""
    return render_template('outliner.html')


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload and return image info"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = app.config['UPLOAD_FOLDER'] / unique_filename
        
        # Save file
        file.save(str(filepath))
        
        # Get image info
        image_info = image_utils.get_image_info(str(filepath))
        
        # Store in session
        session['uploaded_image'] = unique_filename
        session['original_dimensions'] = {
            'width': image_info['width'],
            'height': image_info['height']
        }
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'image_info': image_info,
            'preview_url': f'/static/uploads/{unique_filename}'
        })
    
    except Exception as e:
        app.logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/enhance', methods=['POST'])
def enhance_image():
    """Enhance image with specified parameters"""
    try:
        data = request.get_json()
        
        if 'filename' not in data:
            return jsonify({'error': 'No filename provided'}), 400
        
        filename = data['filename']
        input_path = app.config['UPLOAD_FOLDER'] / filename
        
        if not input_path.exists():
            return jsonify({'error': 'Image file not found'}), 404
        
        # Get enhancement parameters
        target_width = data.get('width')
        target_height = data.get('height')
        ppi_horizontal = data.get('ppi_horizontal', app.config['DEFAULT_PPI'])
        ppi_vertical = data.get('ppi_vertical', app.config['DEFAULT_PPI'])
        maintain_aspect = data.get('maintain_aspect', True)
        output_format = data.get('format', 'png').lower()
        
        # Generate output filename
        output_filename = f"{uuid.uuid4().hex}_enhanced.{output_format}"
        output_path = app.config['ENHANCED_FOLDER'] / output_filename
        
        # Process image
        result = image_processor.enhance_image(
            input_path=str(input_path),
            output_path=str(output_path),
            target_width=target_width,
            target_height=target_height,
            ppi_horizontal=ppi_horizontal,
            ppi_vertical=ppi_vertical,
            maintain_aspect=maintain_aspect
        )
        
        if result['success']:
            session['enhanced_image'] = output_filename
            return jsonify({
                'success': True,
                'enhanced_url': f'/static/enhanced/{output_filename}',
                'original_url': f'/static/uploads/{filename}',
                'output_info': result['output_info']
            })
        else:
            return jsonify({'error': result.get('error', 'Enhancement failed')}), 500
    
    except Exception as e:
        app.logger.error(f"Enhancement error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract-outline', methods=['POST'])
def extract_outline():
    """Extract outline from image"""
    try:
        data = request.get_json()
        
        # Check if using enhanced image or uploading new one
        if 'use_enhanced' in data and data['use_enhanced'] and 'enhanced_image' in session:
            filename = session['enhanced_image']
            input_path = app.config['ENHANCED_FOLDER'] / filename
        elif 'filename' in data:
            filename = data['filename']
            input_path = app.config['UPLOAD_FOLDER'] / filename
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        if not input_path.exists():
            return jsonify({'error': 'Image file not found'}), 404
        
        # Get extraction parameters
        output_format = data.get('format', 'png').lower()
        thickness = data.get('thickness', app.config['OUTLINE_THICKNESS'])
        
        # Generate output filename
        output_filename = f"{uuid.uuid4().hex}_outlined.{output_format}"
        output_path = app.config['OUTLINED_FOLDER'] / output_filename
        
        # Extract outline
        result = outline_extractor.extract_outline(
            input_path=str(input_path),
            output_path=str(output_path),
            thickness=thickness
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'outlined_url': f'/static/outlined/{output_filename}',
                'original_url': f'/static/enhanced/{filename}' if 'use_enhanced' in data else f'/static/uploads/{filename}',
                'output_info': result['output_info']
            })
        else:
            return jsonify({'error': result.get('error', 'Outline extraction failed')}), 500
    
    except Exception as e:
        app.logger.error(f"Outline extraction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<image_type>/<filename>')
def download_image(image_type, filename):
    """Download processed image"""
    try:
        if image_type == 'enhanced':
            folder = app.config['ENHANCED_FOLDER']
        elif image_type == 'outlined':
            folder = app.config['OUTLINED_FOLDER']
        else:
            return jsonify({'error': 'Invalid image type'}), 400
        
        filepath = folder / filename
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            str(filepath),
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        app.logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/calculate-dimensions', methods=['POST'])
def calculate_dimensions():
    """Calculate dimensions based on aspect ratio lock"""
    try:
        data = request.get_json()
        
        original_width = data.get('original_width')
        original_height = data.get('original_height')
        changed_dimension = data.get('changed_dimension')  # 'width' or 'height'
        new_value = data.get('new_value')
        
        if changed_dimension == 'width':
            aspect_ratio = original_height / original_width
            calculated_height = int(new_value * aspect_ratio)
            return jsonify({
                'width': new_value,
                'height': calculated_height
            })
        else:
            aspect_ratio = original_width / original_height
            calculated_width = int(new_value * aspect_ratio)
            return jsonify({
                'width': calculated_width,
                'height': new_value
            })
    
    except Exception as e:
        app.logger.error(f"Dimension calculation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 50MB'}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )