import os
import sys
from pathlib import Path

def get_project_root():
    """Returns the project root directory."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys.executable).parent
    else:
        # Running as script (from src/utils/paths.py -> go up 2 levels)
        return Path(__file__).resolve().parent.parent.parent

def get_assets_dir():
    """Returns the assets directory."""
    root = get_project_root()
    # In development: src/assets
    # In dist (if added as data): assets
    
    # Check if we are in dev or dist
    dev_assets = root / "src" / "assets"
    if dev_assets.exists():
        return dev_assets
        
    return root / "assets"

def get_config_dir():
    return get_project_root() / "src" / "config"

def get_data_dir():
    return get_project_root() / "data"
