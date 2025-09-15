from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from utils.govt_scraper import scrape_all_government_internships
import os
import json
import sqlite3
import hashlib
import secrets
from functools import wraps
from datetime import datetime

# Import your custom modules
from utils.helpers import (
    load_internships_data,
    get_internship_by_id,
    save_uploaded_file,
    format_recommendation_results,
    generate_response,
    init_database,
    hash_password,
    verify_token
)
from utils.resume_parser import parse_resume
from rule_engine.rule_filter import RuleEngine
from ai_matching.similarity import compute_similarity

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/resumes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['DATA_FILE'] = 'data/internships.json'

# Initialize rule engine and database
rule_engine = RuleEngine()
init_database()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(generate_response(False, "Token is missing")), 401
        
        # Verify token
        user = verify_token(token)
        if not user:
            return jsonify(generate_response(False, "Invalid token")), 401
        
        return f(user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    """Home endpoint"""
    return generate_response(True, "Internship Recommender API is running!")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return generate_response(True, "Server is healthy")

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')
        full_name = data.get('full_name')
        
        if not all([email, password, user_type, full_name]):
            return jsonify(generate_response(False, "All fields are required")), 400
        
        if user_type not in ['student', 'government']:
            return jsonify(generate_response(False, "Invalid user type")), 400
        
        # Hash password
        password_hash = hash_password(password)
        auth_token = secrets.token_hex(32)
        
        conn = sqlite3.connect('internship_recommender.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (email, password_hash, user_type, full_name, auth_token) VALUES (?, ?, ?, ?, ?)",
                (email, password_hash, user_type, full_name, auth_token)
            )
            conn.commit()
            
            return jsonify(generate_response(True, "Registration successful", {
                'token': auth_token,
                'user_type': user_type,
                'user_id': cursor.lastrowid
            }))
            
        except sqlite3.IntegrityError:
            return jsonify(generate_response(False, "Email already exists")), 400
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify(generate_response(False, "Registration failed", error=str(e))), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify(generate_response(False, "Email and password are required")), 400
        
        # Simple authentication for demo (in real app, use proper password hashing)
        conn = sqlite3.connect('internship_recommender.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, password_hash, user_type, full_name FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()
        
        # For demo purposes, we'll just check if user exists
        # In real application, verify password properly
        if not user:
            return jsonify(generate_response(False, "Invalid credentials")), 401
        
        # Generate new token
        new_token = secrets.token_hex(32)
        conn = sqlite3.connect('internship_recommender.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET auth_token = ? WHERE id = ?",
            (new_token, user[0])
        )
        conn.commit()
        conn.close()
        
        return jsonify(generate_response(True, "Login successful", {
            'token': new_token,
            'user_type': user[2],
            'user_id': user[0],
            'full_name': user[3]
        }))
        
    except Exception as e:
        return jsonify(generate_response(False, "Login failed", error=str(e))), 500

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Upload resume file"""
    try:
        if 'resume' not in request.files:
            return jsonify(generate_response(False, "No file uploaded")), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify(generate_response(False, "No file selected")), 400
        
        # Save uploaded file
        file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        if not file_path:
            return jsonify(generate_response(False, "Invalid file type")), 400
        
        # Parse resume
        resume_data = parse_resume(file_path)
        
        if 'error' in resume_data:
            return jsonify(generate_response(False, "Error parsing resume", error=resume_data['error'])), 400
        
        return jsonify(generate_response(True, "Resume uploaded successfully", {
            'resume_data': resume_data,
            'file_path': file_path
        }))
        
    except Exception as e:
        return jsonify(generate_response(False, "Server error", error=str(e))), 500

@app.route('/api/internships', methods=['GET'])
def get_internships():
    """Get all internships"""
    try:
        internships = load_internships_data(app.config['DATA_FILE'])
        return jsonify(generate_response(True, "Internships retrieved successfully", {
            'internships': internships,
            'count': len(internships)
        }))
    except Exception as e:
        return jsonify(generate_response(False, "Error loading internships", error=str(e))), 500

@app.route('/api/government/internships/db', methods=['GET'])
def get_government_internships_db():
    """Get all government internships from DATABASE"""
    try:
        conn = sqlite3.connect('internship_recommender.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, department, description, location, duration, 
                   stipend, requirements, application_deadline, created_at
            FROM government_internships 
            ORDER BY created_at DESC
        ''')
        
        internships = []
        for row in cursor.fetchall():
            internships.append({
                'id': row[0],
                'title': row[1],
                'department': row[2],
                'description': row[3],
                'location': row[4],
                'duration': row[5],
                'stipend': row[6],
                'requirements': row[7],
                'application_deadline': row[8],
                'created_at': row[9]
            })
        
        conn.close()
        return jsonify(generate_response(True, "Government internships retrieved", {
            'internships': internships
        }))
        
    except Exception as e:
        return jsonify(generate_response(False, "Error retrieving internships", error=str(e))), 500

@app.route('/api/government/internships', methods=['POST'])
@token_required
def create_government_internship(user):
    """Create new government internship"""
    try:
        data = request.json
        required_fields = ['title', 'department', 'description', 'location', 'duration']
        
        if not all(field in data for field in required_fields):
            return jsonify(generate_response(False, "Missing required fields")), 400
        
        conn = sqlite3.connect('internship_recommender.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO government_internships 
            (title, department, description, location, duration, stipend, requirements, application_deadline, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data['department'],
            data['description'],
            data['location'],
            data['duration'],
            data.get('stipend'),
            data.get('requirements'),
            data.get('application_deadline'),
            user[0]  # user[0] is user_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify(generate_response(True, "Internship created successfully", {
            'internship_id': cursor.lastrowid
        }))
        
    except Exception as e:
        return jsonify(generate_response(False, "Error creating internship", error=str(e))), 500

@app.route('/api/recommend', methods=['POST'])
def recommend_internships():
    """Get internship recommendations based on resume"""
    try:
        data = request.json
        if not data or 'resume_text' not in data:
            return jsonify(generate_response(False, "Resume text is required")), 400
        
        resume_text = data['resume_text']
        internships = load_internships_data(app.config['DATA_FILE'])
        
        recommendations = []
        
        for internship in internships:
            # AI Matching
            similarity_result = compute_similarity(resume_text, internship.get('description', ''))
            
            # Rule-based filtering - TEMPORARY: Skip rule checking for now
            # requirements = internship.get('requirements', {})
            # passes_rule, rule_results = rule_engine.check_minimum_requirements(
            #     {'raw_text': resume_text}, requirements
            # )
            
            # TEMPORARY: Always pass rule check for testing
            passes_rule = True
            rule_results = {"score": 85, "all_checks_passed": True}
            
            recommendations.append({
                'internship': internship,
                'similarity_score': similarity_result['similarity_score'],
                'explanation': similarity_result['explanation'],
                'passes_rule': passes_rule,
                'rule_score': rule_results.get('score', 0),
                'rule_details': rule_results
            })
        
        # Filter and sort recommendations - TEMPORARY: Remove rule filter
        filtered_recommendations = [
            rec for rec in recommendations 
            if rec['similarity_score'] > 0.1  # Lower threshold for testing
        ]
        
        # Sort by similarity score only for now
        filtered_recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Prepare final results
        final_results = []
        for rec in filtered_recommendations[:10]:
            final_results.append({
                'id': rec['internship']['id'],
                'title': rec['internship']['title'],
                'company': rec['internship']['company'],
                'similarity_score': rec['similarity_score'],
                'rule_score': rec['rule_score'],
                'combined_score': round(rec['similarity_score'], 3),
                'explanation': rec['explanation'],
                'location': rec['internship'].get('location'),
                'duration': rec['internship'].get('duration'),
                'stipend': rec['internship'].get('stipend')
            })
        
        return jsonify(generate_response(True, "Recommendations generated successfully", {
            'recommendations': final_results,
            'total_recommendations': len(final_results)
        }))
        
    except Exception as e:
        return jsonify(generate_response(False, "Error generating recommendations", error=str(e))), 500
    
@app.route('/api/internships/government/live', methods=['GET'])
def get_live_government_internships():
    """Get live internships from all government portals"""
    try:
        internships = scrape_all_government_internships()
        return jsonify(generate_response(True, "Government internships retrieved", {
            'internships': internships,
            'count': len(internships),
            'sources': list(set(intern['source'] for intern in internships))
        }))
    except Exception as e:
        return jsonify(generate_response(False, "Error fetching government internships", error=str(e))), 500

@app.route('/api/recommend/government', methods=['POST'])
def recommend_government_internships():
    """Get recommendations from live government internships"""
    try:
        data = request.json
        if not data or 'resume_text' not in data:
            return jsonify(generate_response(False, "Resume text is required")), 400
        
        resume_text = data['resume_text']
        internships = scrape_all_government_internships()
        
        recommendations = []
        
        for internship in internships:
            similarity_result = compute_similarity(resume_text, internship.get('description', ''))
            
            recommendations.append({
                'internship': internship,
                'similarity_score': similarity_result['similarity_score'],
                'explanation': similarity_result['explanation'],
                'combined_score': round(similarity_result['similarity_score'], 3)
            })
        
        # Sort by similarity score
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Prepare final results
        final_results = []
        for rec in recommendations:
            if rec['similarity_score'] > 0.1:
                final_results.append({
                    'title': rec['internship']['title'],
                    'department': rec['internship']['department'],
                    'similarity_score': rec['similarity_score'],
                    'explanation': rec['explanation'],
                    'location': rec['internship'].get('location'),
                    'duration': rec['internship'].get('duration'),
                    'stipend': rec['internship'].get('stipend'),
                    'source': rec['internship'].get('source'),
                    'apply_url': rec['internship'].get('apply_url')
                })
        
        return jsonify(generate_response(True, "Government recommendations generated", {
            'recommendations': final_results,
            'total_recommendations': len(final_results)
        }))
        
    except Exception as e:
        return jsonify(generate_response(False, "Error generating recommendations", error=str(e))), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify(generate_response(False, "Endpoint not found")), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(generate_response(False, "Internal server error")), 500

if __name__ == '__main__':
    print("Starting Internship Recommender API...")
    print("Available endpoints:")
    print("  GET  /api/health")
    print("  POST /api/register")
    print("  POST /api/login")
    print("  POST /api/upload-resume")
    print("  GET  /api/internships")
    print("  GET  /api/government/internships/db")
    print("  POST /api/government/internships")
    print("  POST /api/recommend")
    print("  GET  /api/internships/government/live")
    print("  POST /api/recommend/government")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
