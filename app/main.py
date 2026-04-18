from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from routes.admin_flask import admin_bp
from routes.api_flask import api_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

# Enable CORS
CORS(app)

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')


@app.route('/dashboard/bbl4')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Cricket Heroes API is running"
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"status": "error", "detail": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"status": "error", "detail": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
