import os
import cv2
import numpy as np
from PIL import Image
import base64
import io
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        allowed_extensions = {'png', 'jpg', 'jpeg', 'dicom', 'nii'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def save_uploaded_file(file, upload_folder):
        """Save uploaded file and return path"""
        try:
            filename = file.filename
            filepath = os.path.join(upload_folder, filename)
            
            # Create directory if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file.save(filepath)
            return filepath
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return None
    
    @staticmethod
    def preprocess_image(image_path):
        """Preprocess image for analysis"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Convert to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize for consistency
            resized = cv2.resize(img_rgb, (512, 512))
            
            # Apply slight Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(resized, (3, 3), 0)
            
            # Enhance contrast using CLAHE
            lab = cv2.cvtColor(blurred, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l_enhanced = clahe.apply(l)
            enhanced = cv2.merge([l_enhanced, a, b])
            enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            
            return enhanced_rgb
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    @staticmethod
    def extract_features(image_path):
        """Extract relevant features from MRI image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {}
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Basic statistics
            mean_intensity = float(np.mean(gray))
            std_intensity = float(np.std(gray))
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = float(np.sum(edges > 0) / edges.size)
            
            # Texture analysis (simple)
            from skimage.feature import graycomatrix, graycoprops
            try:
                glcm = graycomatrix(gray, [1], [0], 256, symmetric=True, normed=True)
                contrast = graycoprops(glcm, 'contrast')[0, 0]
                homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
            except:
                contrast = 0
                homogeneity = 0
            
            return {
                'mean_intensity': round(mean_intensity, 2),
                'std_intensity': round(std_intensity, 2),
                'edge_density': round(edge_density, 4),
                'contrast': round(float(contrast), 2),
                'homogeneity': round(float(homogeneity), 4),
                'dimensions': img.shape[:2]
            }
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    @staticmethod
    def image_to_base64(image_path):
        """Convert image to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting to base64: {e}")
            return None
    
    @staticmethod
    def cleanup_uploaded_files(upload_folder, keep_latest=10):
        """Clean up old uploaded files to save space"""
        try:
            files = [os.path.join(upload_folder, f) for f in os.listdir(upload_folder) 
                    if os.path.isfile(os.path.join(upload_folder, f))]
            files.sort(key=os.path.getmtime, reverse=True)
            
            # Delete old files beyond keep_latest
            for file in files[keep_latest:]:
                os.remove(file)
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")