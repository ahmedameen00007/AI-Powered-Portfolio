import sys
from pathlib import Path

# Add project root and Ovi folder to sys.path so server can find its modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Ovi"))

# Import the Flask application instance
from Ovi.server import app
