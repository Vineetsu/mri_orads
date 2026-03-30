from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from werkzeug.utils import secure_filename
import json
from datetime import datetime

from config import Config
from utils.image_processor import ImageProcessor
from utils.groq_client import GroqClient

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

CORS(app)

# Initialize components
image_processor = ImageProcessor()
groq_client = GroqClient()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_images():
    """Endpoint to analyze uploaded MRI images"""
    try:
        # Check if files were uploaded
        if 'images' not in request.files:
            return jsonify({'error': 'No images uploaded'}), 400
        
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No images selected'}), 400
        
        # Process each image
        uploaded_files = []
        image_features_list = []
        
        for file in files:
            if file and image_processor.allowed_file(file.filename):
                # Secure filename and save
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = image_processor.save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
                
                if filepath:
                    uploaded_files.append(filepath)
                    
                    # Extract features
                    features = image_processor.extract_features(filepath)
                    if features:
                        image_features_list.append(features)
        
        if not uploaded_files:
            return jsonify({'error': 'No valid images uploaded'}), 400
        
        # Analyze with Groq
        if len(uploaded_files) == 1:
            # Single image analysis
            analysis = groq_client.analyze_mri_image(image_features_list[0] if image_features_list else {})
        else:
            # Multiple images analysis
            analysis = groq_client.analyze_mri_image(image_features_list, is_multiple=True)
        
        # Add O-RADS risk category details
        if 'orads_score' in analysis:
            score = analysis['orads_score']
            orads_info = Config.ORADS_RISK.get(score, Config.ORADS_RISK[3])
            analysis['risk_details'] = {
                'risk_percentage': orads_info['risk'],
                'risk_level': orads_info['level'],
                'risk_color': orads_info['color']
            }
        
        # Clean up uploaded files (optional)
        # image_processor.cleanup_uploaded_files(app.config['UPLOAD_FOLDER'])
        
        # Return analysis results
        return jsonify({
            'success': True,
            'analysis': analysis,
            'images_processed': len(uploaded_files),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in analysis endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'groq_configured': bool(Config.GROQ_API_KEY)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)