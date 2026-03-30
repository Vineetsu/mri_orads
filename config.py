import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = "mixtral-8x7b-32768"  # You can change this to any Groq model
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dicom', 'nii'}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # O-RADS Risk Categories
    ORADS_RISK = {
        1: {'risk': '<1%', 'level': 'Benign', 'color': '#10B981'},
        2: {'risk': '<1%', 'level': 'Benign', 'color': '#10B981'},
        3: {'risk': '1-10%', 'level': 'Low Risk', 'color': '#F59E0B'},
        4: {'risk': '10-50%', 'level': '⚠️ Suspicious', 'color': '#EF4444'},
        5: {'risk': '≥50%', 'level': '🚨 High Suspicion', 'color': '#DC2626'}
    }