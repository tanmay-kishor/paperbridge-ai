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

    # Use configured frontend origins in development/production.
    # Defaults to wildcard "*" to support all Vercel domains, preview branches, and localhost.
    CORS(
        app,
        resources={r"/*": {"origins": Config.CORS_ORIGINS}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "OPTIONS"]
    )

    @app.errorhandler(Exception)
    def handle_global_error(e):
        logger.exception(f"Unhandled exception in API request: {e}")
        resp = jsonify({
            "error": "Internal API processing notice",
            "message": str(e)
        })
        resp.status_code = 500
        return resp

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return jsonify({
            "message": "Welcome to PaperBridge AI API",
            "documentation": "/docs/architecture.md",
            "healthcheck": "/api/health",
            "search_endpoint": "/api/search",
            "status": "healthy"
        })

    return app

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting PaperBridge AI Backend on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=False, use_reloader=False)
