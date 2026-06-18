"""
Simple Flask application for Azure Web App deployment.
"""
from flask import Flask, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)


@app.route('/')
def home():
    """Home endpoint returning HTML with app status."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Azure Flask App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { background: #e8f5e9; padding: 20px; border-radius: 5px; }
            .info { margin-top: 20px; font-size: 14px; color: #666; }
        </style>
    </head>
    <body>
        <h1>🚀 Flask App Running on Azure</h1>
        <div class="status">
            <p><strong>Status:</strong> ✓ Healthy</p>
            <p><strong>Server:</strong> Gunicorn</p>
            <p><strong>Environment:</strong> ''' + os.getenv('ENVIRONMENT', 'production') + '''</p>
            <p><strong>Timestamp:</strong> ''' + datetime.utcnow().isoformat() + '''</p>
        </div>
        <div class="info">
            <p>Available endpoints:</p>
            <ul>
                <li><code>GET /</code> - This page</li>
                <li><code>GET /health</code> - Health check (JSON)</li>
                <li><code>GET /api/info</code> - App info (JSON)</li>
                <li><code>POST /api/echo</code> - Echo request body (JSON)</li>
            </ul>
        </div>
    </body>
    </html>
    '''


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Azure monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'flask-app'
    }), 200


@app.route('/api/info', methods=['GET'])
def get_info():
    """Return app information."""
    return jsonify({
        'app': 'Azure Flask Demo',
        'version': '1.0.0',
        'environment': os.getenv('ENVIRONMENT', 'production'),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/echo', methods=['POST'])
def echo():
    """Echo the request body back."""
    data = request.get_json() or {}
    return jsonify({
        'message': 'Echo endpoint',
        'received': data,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/greet', methods=['GET'])
def greet():
    """Simple greeting endpoint with optional name parameter."""
    name = request.args.get('name', 'World')
    return jsonify({
        'greeting': f'Hello, {name}!',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
