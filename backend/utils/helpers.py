import os
import json
import logging
import sqlite3
import hashlib
import secrets
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load internships data
def load_internships_data(file_path: str) -> List[Dict]:
    """Load internships data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('internships', [])
    except Exception as e:
        logger.error(f"Error loading internships data: {e}")
        return []

def get_internship_by_id(internships: List[Dict], internship_id: str) -> Optional[Dict]:
    """Get internship by ID"""
    for internship in internships:
        if internship.get('id') == internship_id:
            return internship
    return None

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    allowed_extensions = {'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder: str) -> str:
    """Save uploaded file and return file path"""
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            return file_path
        return None
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

def format_recommendation_results(internships: List[Dict], scores: List[float]) -> List[Dict]:
    """Format recommendation results with ranking"""
    results = []
    for internship, score in zip(internships, scores):
        results.append({
            'id': internship.get('id'),
            'title': internship.get('title'),
            'company': internship.get('company'),
            'similarity_score': round(score, 3),
            'location': internship.get('location'),
            'duration': internship.get('duration'),
            'stipend': internship.get('stipend'),
            'apply_link': internship.get('apply_link')
        })
    
    # Sort by similarity score descending
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Add ranking
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    return results

def generate_response(success: bool, message: str, data: Any = None, error: str = None) -> Dict:
    """Generate standardized API response"""
    response = {
        'success': success,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    if error is not None:
        response['error'] = error
    
    return response

# Database functions
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('internship_recommender.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        user_type TEXT NOT NULL CHECK(user_type IN ('student', 'government')),
        full_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        auth_token TEXT
    )
    ''')
    
    # Government internships table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS government_internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        department TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT NOT NULL,
        duration TEXT NOT NULL,
        stipend TEXT,
        requirements TEXT,
        application_deadline DATE,
        created_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_token(token):
    """Verify authentication token"""
    try:
        conn = sqlite3.connect('internship_recommender.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, user_type, full_name FROM users WHERE auth_token = ?",
            (token,)
        )
        user = cursor.fetchone()
        conn.close()
        return user
    except:
        return None
