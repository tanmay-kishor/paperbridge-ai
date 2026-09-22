"""
PaperBridge AI - Root Application Entry Point
For cloud platforms that execute gunicorn app:app from the repository root.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.app import app

if __name__ == "__main__":
    app.run()
