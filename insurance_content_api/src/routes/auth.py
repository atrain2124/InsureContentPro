from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.insurance_models import db, Agent, SubscriptionStatus
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new agent"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if agent already exists
        existing_agent = Agent.query.filter_by(email=email).first()
        if existing_agent:
            return jsonify({'error': 'Agent with this email already exists'}), 409
        
        # Create new agent
        password_hash = generate_password_hash(password)
        trial_end = datetime.utcnow() + timedelta(days=7)
        
        new_agent = Agent(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            subscription_status=SubscriptionStatus.TRIAL,
            trial_start_date=datetime.utcnow(),
            trial_end_date=trial_end
        )
        
        db.session.add(new_agent)
        db.session.commit()
        
        # Set session
        session['agent_id'] = new_agent.id
        session['agent_email'] = new_agent.email
        
        return jsonify({
            'message': 'Agent registered successfully',
            'agent': new_agent.to_dict(),
            'trial_days_remaining': 7
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login an existing agent"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find agent
        agent = Agent.query.filter_by(email=email).first()
        if not agent or not check_password_hash(agent.password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Set session
        session['agent_id'] = agent.id
        session['agent_email'] = agent.email
        
        # Calculate trial days remaining
        trial_days_remaining = 0
        if agent.subscription_status == SubscriptionStatus.TRIAL:
            remaining = agent.trial_end_date - datetime.utcnow()
            trial_days_remaining = max(0, remaining.days)
        
        return jsonify({
            'message': 'Login successful',
            'agent': agent.to_dict(),
            'trial_days_remaining': trial_days_remaining,
            'subscription_active': agent.is_subscription_active()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout the current agent"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_agent():
    """Get current agent information"""
    try:
        agent_id = session.get('agent_id')
        if not agent_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        agent = Agent.query.get(agent_id)
        if not agent:
            session.clear()
            return jsonify({'error': 'Agent not found'}), 404
        
        # Calculate trial days remaining
        trial_days_remaining = 0
        if agent.subscription_status == SubscriptionStatus.TRIAL:
            remaining = agent.trial_end_date - datetime.utcnow()
            trial_days_remaining = max(0, remaining.days)
        
        return jsonify({
            'agent': agent.to_dict(),
            'trial_days_remaining': trial_days_remaining,
            'subscription_active': agent.is_subscription_active()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get agent information', 'details': str(e)}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
def update_profile():
    """Update agent profile"""
    try:
        agent_id = session.get('agent_id')
        if not agent_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            agent.first_name = data['first_name'].strip()
        if 'last_name' in data:
            agent.last_name = data['last_name'].strip()
        if 'insurance_types' in data:
            agent.set_insurance_types(data['insurance_types'])
        if 'default_tone' in data:
            from src.models.insurance_models import ToneType
            try:
                agent.default_tone = ToneType(data['default_tone'])
            except ValueError:
                return jsonify({'error': 'Invalid tone type'}), 400
        
        agent.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        agent_id = session.get('agent_id')
        if not agent_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        agent = Agent.query.get(agent_id)
        if not agent:
            session.clear()
            return jsonify({'error': 'Agent not found'}), 404
        
        return f(agent, *args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_active_subscription(f):
    """Decorator to require active subscription"""
    def decorated_function(agent, *args, **kwargs):
        if not agent.is_subscription_active():
            return jsonify({
                'error': 'Active subscription required',
                'subscription_status': agent.subscription_status.value,
                'trial_expired': not agent.is_trial_active()
            }), 403
        
        return f(agent, *args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function
