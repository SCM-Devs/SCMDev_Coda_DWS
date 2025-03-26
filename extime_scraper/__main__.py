"""
Allows running the package as a module with python -m extime_scraper
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path to allow module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extime_scraper.main import main

if __name__ == "__main__":
    main()
