import os
import sys
from datetime import datetime, timedelta
import hashlib
import secrets
import json

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
content_schedules = {}

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against provided password."""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def generate_demo_content(insurance_types, tone, custom_instructions=""):
    """Generate demo content based on user preferences."""
    
    # Sample content templates based on insurance types
    content_templates = {
        'mortgage_protection': [
            "🏠 Your home is likely your biggest investment. Protect it with mortgage protection insurance that ensures your family can stay in their home even if the unexpected happens. #MortgageProtection #HomeInsurance #FamilyFirst",
            "💡 Did you know? Mortgage protection insurance is different from PMI. It pays off your mortgage if you pass away, giving your family peace of mind. #InsuranceEducation #MortgageProtection",
            "🔒 Secure your family's future with mortgage protection. It's not just about the house - it's about keeping your loved ones safe and secure. #FamilySecurity #MortgageInsurance"
        ],
        'index_universal_life': [
            "📈 Index Universal Life insurance offers the best of both worlds: life insurance protection AND cash value growth tied to market performance with downside protection. #IUL #LifeInsurance #WealthBuilding",
            "💰 Building wealth while protecting your family? That's the power of Index Universal Life. Tax-free growth potential with a safety net. #TaxFreeGrowth #IUL #RetirementPlanning",
            "🎯 Smart money moves: IUL policies can provide retirement income, life insurance, and tax advantages all in one package. #SmartMoney #IUL #FinancialPlanning"
        ],
        'term_life_living_benefits': [
            "⚡ Modern term life insurance isn't just for when you're gone. Living benefits let you access your policy if you face a critical illness. #LivingBenefits #TermLife #CriticalIllness",
            "🛡️ Term life with living benefits: Protection for your family AND financial help if you face cancer, heart attack, or stroke. #LifeInsurance #LivingBenefits #HealthProtection",
            "💪 Why wait? Living benefits in term life policies mean you can use your insurance while you're alive to fight illness and recover. #LivingBenefits #TermLife"
        ],
        'final_expense': [
            "🕊️ Final expense insurance ensures your loved ones won't be burdened with funeral costs during their time of grief. Small premiums, big peace of mind. #FinalExpense #LifeInsurance #FamilyCare",
            "💝 The greatest gift you can give your family is not leaving them with bills. Final expense coverage takes care of everything. #FinalExpense #FamilyFirst #PeaceOfMind",
            "📋 Final expense insurance: Guaranteed acceptance, affordable premiums, and the assurance that your final wishes will be honored. #FinalExpense #GuaranteedAcceptance"
        ],
        'annuities': [
            "🏦 Worried about outliving your money? Annuities provide guaranteed income for life, no matter how long you live. #Annuities #RetirementIncome #GuaranteedIncome",
            "📊 Market volatility got you worried about retirement? Fixed annuities offer guaranteed growth and protection from market downturns. #FixedAnnuities #RetirementSecurity #GuaranteedGrowth",
            "🎯 Annuities aren't just for retirement - they're for anyone who wants guaranteed, predictable income they can count on. #Annuities #FinancialSecurity #PredictableIncome"
        ],
        'health_insurance': [
            "🏥 Health insurance isn't just about doctor visits - it's about protecting your financial future from unexpected medical bills. #HealthInsurance #MedicalBills #FinancialProtection",
            "💊 The right health insurance plan can save you thousands. Let me help you find coverage that fits your needs and budget. #HealthInsurance #AffordableCare #HealthCoverage",
            "🩺 Open enrollment is coming! Don't wait until you need it to think about health insurance. Prevention is always better than cure. #OpenEnrollment #HealthInsurance #Prevention"
        ]
    }
    
    # Image prompts for different insurance types
    image_prompts = {
        'mortgage_protection': [
            "A happy family standing in front of their beautiful home with a protective shield overlay",
            "A house with a safety umbrella protecting it from storm clouds",
            "A family key with a heart-shaped keychain in front of a cozy home"
        ],
        'index_universal_life': [
            "A growing tree with dollar signs as leaves and strong roots",
            "A graph showing upward growth with a safety net underneath",
            "A piggy bank with wings flying upward with coins trailing behind"
        ],
        'term_life_living_benefits': [
            "A strong shield protecting a family silhouette with a medical cross",
            "A life preserver ring with a medical stethoscope around it",
            "A superhero cape with a medical cross emblem"
        ],
        'final_expense': [
            "A peaceful dove carrying a small gift box with a ribbon",
            "Gentle hands holding a small treasure chest with soft lighting",
            "A serene sunset with a small memorial candle and flowers"
        ],
        'annuities': [
            "A steady stream of golden coins flowing into a secure vault",
            "A reliable clock with dollar signs marking the hours",
            "A strong foundation with money growing like a garden on top"
        ],
        'health_insurance': [
            "A medical stethoscope forming a heart shape with a family inside",
            "A protective medical cross shield covering a happy family",
            "A doctor's hands holding a miniature family with care"
        ]
    }
    
    # Generate posts for the week
    posts = []
    post_id = 1
    
    # Get current date and generate for next 7 days
    start_date = datetime.now()
    
    for i in range(7):
        post_date = start_date + timedelta(days=i)
        
        # Select insurance type for this post
        if insurance_types:
            selected_type = insurance_types[i % len(insurance_types)]
        else:
            selected_type = 'mortgage_protection'  # Default
        
        # Get content template
        templates = content_templates.get(selected_type, content_templates['mortgage_protection'])
        content = templates[i % len(templates)]
        
        # Adjust tone
        if tone == 'urgent':
            content = "🚨 URGENT: " + content + " Don't wait - protect your family today!"
        elif tone == 'funny':
            content = content.replace('Did you know?', 'Fun fact:').replace('🏠', '🏠😄').replace('💡', '💡😂')
        elif tone == 'direct':
            content = content.replace('?', '.').replace('🎯', '➡️')
        
        # Add custom instructions if provided
        if custom_instructions:
            content += f" {custom_instructions}"
        
        # Get image prompt
        prompts = image_prompts.get(selected_type, image_prompts['mortgage_protection'])
        image_prompt = prompts[i % len(prompts)]
        
        # Extract hashtags
        hashtags = [tag for tag in content.split() if tag.startswith('#')]
        
        post = {
            'id': post_id,
            'date': post_date.strftime('%Y-%m-%d'),
            'day_name': post_date.strftime('%A'),
            'text': content,
            'hashtags': hashtags,
            'image_prompt': image_prompt,
            'image_url': None,
            'insurance_type': selected_type,
            'tone': tone
        }
        
        posts.append(post)
        post_id += 1
    
    return posts

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

# Content generation endpoint
@app.route('/api/content/generate', methods=['POST'])
def generate_content():
    try:
        user_id = session.get('user_id')
        email = session.get('email')
        
        if not user_id or not email or email not in users:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        insurance_types = data.get('insurance_types', [])
        tone = data.get('tone', 'professional')
        custom_instructions = data.get('custom_instructions', '')
        week_start = data.get('week_start', datetime.now().strftime('%Y-%m-%d'))
        
        # Generate content
        posts = generate_demo_content(insurance_types, tone, custom_instructions)
        
        # Store the schedule
        schedule_id = secrets.token_urlsafe(16)
        content_schedules[schedule_id] = {
            'id': schedule_id,
            'user_id': user_id,
            'week_start': week_start,
            'insurance_types': insurance_types,
            'tone': tone,
            'custom_instructions': custom_instructions,
            'posts': posts,
            'created_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'schedule_id': schedule_id,
            'week_start': week_start,
            'posts': posts,
            'message': 'Content schedule generated successfully!'
        }), 200
        
    except Exception as e:
        print(f"Content generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate content. Please try again.'}), 500

# Get user's content schedules
@app.route('/api/content/schedules', methods=['GET'])
def get_schedules():
    try:
        user_id = session.get('user_id')
        email = session.get('email')
        
        if not user_id or not email or email not in users:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get user's schedules
        user_schedules = []
        for schedule_id, schedule in content_schedules.items():
            if schedule['user_id'] == user_id:
                user_schedules.append({
                    'id': schedule['id'],
                    'week_start': schedule['week_start'],
                    'created_at': schedule['created_at'],
                    'post_count': len(schedule['posts']),
                    'insurance_types': schedule['insurance_types'],
                    'tone': schedule['tone']
                })
        
        # Sort by creation date (newest first)
        user_schedules.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'schedules': user_schedules
        }), 200
        
    except Exception as e:
        print(f"Get schedules error: {str(e)}")
        return jsonify({'error': 'Failed to get schedules'}), 500

# Get specific schedule
@app.route('/api/content/schedules/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    try:
        user_id = session.get('user_id')
        email = session.get('email')
        
        if not user_id or not email or email not in users:
            return jsonify({'error': 'Not authenticated'}), 401
        
        if schedule_id not in content_schedules:
            return jsonify({'error': 'Schedule not found'}), 404
        
        schedule = content_schedules[schedule_id]
        
        # Check if user owns this schedule
        if schedule['user_id'] != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(schedule), 200
        
    except Exception as e:
        print(f"Get schedule error: {str(e)}")
        return jsonify({'error': 'Failed to get schedule'}), 500

# Subscription endpoints (demo)
@app.route('/api/subscription/pricing', methods=['GET'])
def get_pricing():
    return jsonify({
        'plans': [
            {
                'id': 'monthly',
                'name': 'Monthly Plan',
                'price': 29.97,
                'interval': 'month',
                'features': [
                    'Unlimited weekly content generation',
                    'AI-powered image creation',
                    'Multiple insurance types',
                    'Custom tone options',
                    'Copy & share functionality',
                    'Email support'
                ]
            },
            {
                'id': 'annual',
                'name': 'Annual Plan',
                'price': 299.97,
                'interval': 'year',
                'savings': 60,
                'features': [
                    'All monthly plan features',
                    '$60 annual savings',
                    'Priority support',
                    'Early access to new features'
                ]
            }
        ],
        'trial_days': 7
    })

@app.route('/api/subscription/status', methods=['GET'])
def get_subscription_status():
    try:
        user_id = session.get('user_id')
        email = session.get('email')
        
        if not user_id or not email or email not in users:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = users[email]
        
        # Calculate trial days remaining
        trial_end = datetime.fromisoformat(user['trial_end'])
        days_remaining = max(0, (trial_end - datetime.utcnow()).days)
        
        return jsonify({
            'status': user['subscription_status'],
            'trial_end': user['trial_end'],
            'days_remaining': days_remaining,
            'can_generate_content': days_remaining > 0 or user['subscription_status'] == 'ACTIVE'
        }), 200
        
    except Exception as e:
        print(f"Get subscription status error: {str(e)}")
        return jsonify({'error': 'Failed to get subscription status'}), 500

if __name__ == '__main__':
    print("🚀 Starting InsureContent Pro Local Development Server...")
    print("📍 Backend API: http://localhost:5000")
    print("🎯 Frontend: http://localhost:5173")
    print("📚 API Documentation: http://localhost:5000/api/health")
    print("\n✨ Features enabled:")
    print("   - User registration and authentication")
    print("   - AI-powered content generation")
    print("   - Content schedule management")
    print("   - Subscription status tracking")
    print("   - Full React frontend integration")
    print("\n🔧 Ready for testing!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
