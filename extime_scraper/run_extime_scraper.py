"""
Entry point script to run the Extime scraper.
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path to ensure package is importable
sys.path.insert(0, str(Path(__file__).parent))

# Import directly from the module
from extime_scraper.main import main

if __name__ == "__main__":
    main()
