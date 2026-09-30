"""
PaperBridge AI - Root Application Entry Point
Supports cloud platforms (Render, Railway, Heroku) starting the app via `app:app` or `backend.app:app`.
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app

if __name__ == "__main__":
    app.run()
