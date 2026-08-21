import sys
import os
from pathlib import Path

# Make the Ovi folder importable as a package root
ovi_dir = Path(__file__).resolve().parent.parent / "Ovi"
sys.path.insert(0, str(ovi_dir))

# Set working dir so relative paths in server.py (dataset/indexes etc.) resolve correctly
os.chdir(str(ovi_dir))

# Import the Flask app — Vercel will expose this as the serverless function
from server import app
