"""
PaperBridge AI - Backend Configuration
Contains system-wide settings, API endpoints, rate limiters, and security parameters.
"""

import os

class Config:
    # Security: Server Host & Port
    HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
    PORT = int(os.environ.get("FLASK_PORT", 5000))
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")

    # Security: CORS Allowed Origins
    # Restrict to local development & production frontend origins
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")

    # Semantic Scholar API Settings
    # Public endpoint supports up to 100 requests per 5 minutes without key
    SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", None)
    S2_BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    # Unpaywall API Settings
    # Unpaywall requires a valid contact email for fair use tracking
    UNPAYWALL_EMAIL = os.environ.get("UNPAYWALL_EMAIL", "paperbridge.prototype@student.edu")
    UNPAYWALL_BASE_URL = "https://api.unpaywall.org/v2"

    # NLP Model Settings
    # 'all-MiniLM-L6-v2' maps sentences & paragraphs to a 384 dimensional dense vector space.
    # It is chosen for fast CPU inference (~22M parameters) without requiring expensive GPU hardware.
    EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    # Security / Sanitization Limits
    MAX_QUERY_LENGTH = 300
    DEFAULT_RESULT_LIMIT = 10
    MAX_RESULT_LIMIT = 30

    # Path to offline sample datasets
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
    if not os.path.exists(DATA_DIR):
        DATA_DIR = os.path.join(BASE_DIR, "data")
    SAMPLE_PAPERS_PATH = os.path.join(DATA_DIR, "test_papers.json")
    SAMPLE_QUERIES_PATH = os.path.join(DATA_DIR, "sample_queries.json")
