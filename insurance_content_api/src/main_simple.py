import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'insurance_content_platform_secret_key_2024'

# Enable CORS for all routes
CORS(app, supports_credentials=True)

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

# Basic API endpoints for demo
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
