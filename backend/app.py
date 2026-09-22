"""
PaperBridge AI - Flask Application Entry Point
Initializes the Flask server, registers CORS policies, and mounts the API blueprint.
"""

import os
import sys
import logging

# Ensure project root is on Python sys.path so modules import reliably
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.api import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("paperbridge")

def create_app(config_class=Config):
    """
    Application factory pattern for PaperBridge AI backend.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for the specified origins
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},  # Permissive for local prototype demo
        supports_credentials=True
    )

    # Register blueprints
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return jsonify({
            "message": "Welcome to PaperBridge AI API",
            "documentation": "/docs/architecture.md",
            "healthcheck": "/api/health",
            "search_endpoint": "/api/search"
        })

    return app

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting PaperBridge AI Backend on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=False, use_reloader=False)
