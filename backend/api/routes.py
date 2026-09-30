"""
PaperBridge AI API Routes
Exposes endpoints for health checking, paper search, and sample queries.
Includes input sanitization and secure error responses.
"""

import json
import logging
import os
import re
from flask import request, jsonify
from backend.api import api_bp
from backend.config import Config

logger = logging.getLogger(__name__)

# Regular expression pattern to validate standard Digital Object Identifiers (DOIs)
# Standard DOI format starts with 10. followed by 4-9 digits, a slash, and arbitrary allowed characters.
DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")

@api_bp.route("/health", methods=["GET"])
def health():
    """
    Healthcheck endpoint to verify server status, version, and CORS connectivity.
    """
    return jsonify({
        "status": "healthy",
        "service": "PaperBridge AI API",
        "version": "1.0.0",
        "cors_origins": Config.CORS_ORIGINS
    }), 200

@api_bp.route("/samples", methods=["GET"])
def get_samples():
    """
    Returns pre-configured sample queries and benchmark datasets for rapid testing.
    """
    try:
        if os.path.exists(Config.SAMPLE_QUERIES_PATH):
            with open(Config.SAMPLE_QUERIES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify(data), 200
        return jsonify({"queries": []}), 200
    except Exception as e:
        logger.error(f"Failed to load sample queries: {e}")
        return jsonify({"error": "Failed to load samples"}), 500

@api_bp.route("/search", methods=["POST"])
def search():
    """
    Core search endpoint.
    Accepts JSON body:
      - query (str): Search topic or paper title / DOI
      - mode (str): 'topic' or 'paper' (defaults to 'topic')
      - limit (int): Max candidate papers to retrieve (default 10)
    
    Security & Sanitization:
      - Enforces string type and max length on query to prevent DoS payloads.
      - Strips control characters.
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request payload. Expected JSON object."}), 400

    query = data.get("query", "").strip()
    mode = data.get("mode", "topic").strip().lower()
    limit = data.get("limit", Config.DEFAULT_RESULT_LIMIT)

    # Input validation & sanitization
    if not query:
        return jsonify({"error": "Query string cannot be empty."}), 400

    if len(query) > Config.MAX_QUERY_LENGTH:
        return jsonify({"error": f"Query exceeds maximum allowed length of {Config.MAX_QUERY_LENGTH} characters."}), 400

    try:
        limit = max(1, min(int(limit), Config.MAX_RESULT_LIMIT))
    except (ValueError, TypeError):
        limit = Config.DEFAULT_RESULT_LIMIT

    if mode not in ("topic", "paper"):
        mode = "topic"

    # Invoke the recommendation pipeline.
    #
    # NOTE: this used to catch bare `ImportError` and silently return a fake
    # "hello world" scaffold response whenever ANY import inside the pipeline
    # failed -- including unrelated dependency problems (e.g. a missing/broken
    # textstat or sentence-transformers install). That meant a broken environment
    # could make every single search return identical fake data with no visible
    # error, which is indistinguishable from "working" unless you read server logs.
    # The pipeline is fully implemented now, so real errors should surface as a
    # proper 500 with a logged traceback instead of being masked.
    try:
        from backend.pipeline.ranker import run_pipeline
    except ModuleNotFoundError as e:
        # Only true if the ranker module file itself is missing/misplaced --
        # a real setup problem, not something to hide behind fake data.
        logger.exception(f"Pipeline module could not be found: {e}")
        return jsonify({
            "error": "Search pipeline is not available on this server (module not found).",
            "detail": str(e)
        }), 500

    try:
        response_data = run_pipeline(query=query, mode=mode, limit=limit)
        return jsonify(response_data), 200
    except Exception as e:
        logger.exception(f"Error executing recommendation search: {e}")
        return jsonify({
            "error": "An internal error occurred while processing your search.",
            "detail": str(e)
        }), 500
