import os
import sys
from pathlib import Path

script_dir = Path(__file__).parent.absolute()

sys.path.insert(0, str(script_dir))

from extime_scraper.main import main

if __name__ == "__main__":
    print(f"Running Extime scraper from {script_dir}")
    main()
