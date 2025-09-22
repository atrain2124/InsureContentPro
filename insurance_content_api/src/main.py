import os
import sys
from datetime import datetime, timedelta
import hashlib
import secrets

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'insurance_content_platform_secret_key_2024'

# Enable CORS for all routes
CORS(app, supports_credentials=True)

# Simple in-memory storage for demo (in production, use a real database)
users = {}
sessions = {}

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against provided password."""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

# Serve React frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files or fallback to index.html for React routing"""
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        # Fallback to index.html for React Router
        return send_from_directory(app.static_folder, 'index.html')

# API endpoints
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'InsureContent Pro API is running'})

@app.route('/api/content/insurance-types')
def get_insurance_types():
    return jsonify({
        'insurance_types': [
            {'value': 'mortgage_protection', 'label': 'Mortgage Protection'},
            {'value': 'index_universal_life', 'label': 'Index Universal Life'},
            {'value': 'term_life_living_benefits', 'label': 'Term Life with Living Benefits'},
            {'value': 'final_expense', 'label': 'Final Expense'},
            {'value': 'annuities', 'label': 'Annuities'},
            {'value': 'health_insurance', 'label': 'Health Insurance'}
        ]
    })

@app.route('/api/content/tones')
def get_tones():
    return jsonify({
        'tones': [
            {'value': 'professional', 'label': 'Professional'},
            {'value': 'friendly', 'label': 'Friendly'},
            {'value': 'direct', 'label': 'Direct'},
            {'value': 'serious', 'label': 'Serious'},
            {'value': 'funny', 'label': 'Funny'},
            {'value': 'urgent', 'label': 'Urgent'}
        ]
    })

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Validation
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if email in users:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create user
        user_id = secrets.token_urlsafe(16)
        users[email] = {
            'id': user_id,
            'email': email,
            'name': name,
            'password': hash_password(password),
            'created_at': datetime.utcnow().isoformat(),
            'trial_start': datetime.utcnow().isoformat(),
            'trial_end': (datetime.utcnow() + timedelta(days=7)).isoformat(),
            'subscription_status': 'TRIAL'
        }
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        sessions[session_token] = {
            'user_id': user_id,
            'email': email,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Set session cookie
        session['user_id'] = user_id
        session['email'] = email
        
        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'subscription_status': 'TRIAL',
                'trial_end': users[email]['trial_end']
            },
            'session_token': session_token
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if email not in users:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = users[email]
        if not verify_password(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        sessions[session_token] = {
            'user_id': user['id'],
            'email': email,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Set session cookie
        session['user_id'] = user['id']
        session['email'] = email
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': email,
                'name': user['name'],
                'subscription_status': user['subscription_status'],
                'trial_end': user.get('trial_end')
            },
            'session_token': session_token
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    try:
        user_id = session.get('user_id')
        email = session.get('email')
        
        if not user_id or not email or email not in users:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = users[email]
        return jsonify({
            'user': {
                'id': user['id'],
                'email': email,
                'name': user['name'],
                'subscription_status': user['subscription_status'],
                'trial_end': user.get('trial_end')
            }
        }), 200
        
    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

# Content generation endpoint (demo)
@app.route('/api/content/generate', methods=['POST'])
def generate_content():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        insurance_types = data.get('insurance_types', [])
        tone = data.get('tone', 'professional')
        custom_instructions = data.get('custom_instructions', '')
        
        # Demo content generation (replace with actual AI integration)
        demo_posts = [
            {
                'id': 1,
                'date': '2024-09-23',
                'text': f'🏠 Protecting your family\'s future starts with the right insurance coverage. As a {tone} insurance professional, I help families secure their most valuable asset - their home and loved ones. #InsuranceProtection #FamilyFirst #MortgageProtection',
                'hashtags': ['#InsuranceProtection', '#FamilyFirst', '#MortgageProtection'],
                'image_prompt': 'A happy family standing in front of their home with a protective shield overlay',
                'image_url': None
            },
            {
                'id': 2,
                'date': '2024-09-24',
                'text': f'💡 Did you know that term life insurance can provide living benefits? Let me show you how modern life insurance policies can protect you while you\'re alive, not just when you\'re gone. #LifeInsurance #LivingBenefits #FinancialPlanning',
                'hashtags': ['#LifeInsurance', '#LivingBenefits', '#FinancialPlanning'],
                'image_prompt': 'A lightbulb with dollar signs inside, representing financial wisdom',
                'image_url': None
            },
            {
                'id': 3,
                'date': '2024-09-25',
                'text': f'🎯 Retirement planning isn\'t just about saving money - it\'s about creating guaranteed income streams. Index Universal Life policies offer growth potential with downside protection. #RetirementPlanning #IUL #FinancialSecurity',
                'hashtags': ['#RetirementPlanning', '#IUL', '#FinancialSecurity'],
                'image_prompt': 'A target with arrows hitting the bullseye, representing financial goals',
                'image_url': None
            }
        ]
        
        return jsonify({
            'schedule_id': secrets.token_urlsafe(16),
            'week_start': '2024-09-23',
            'posts': demo_posts,
            'message': 'Content schedule generated successfully!'
        }), 200
        
    except Exception as e:
        print(f"Content generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate content. Please try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
