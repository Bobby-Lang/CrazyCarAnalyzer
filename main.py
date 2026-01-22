import sys
import os
from pathlib import Path

# Add src to path to ensure imports work if run directly
root = Path(__file__).resolve().parent
sys.path.append(str(root))

from src.gui.main_window import App
from src.utils.paths import get_data_dir, get_config_dir

def ensure_dirs():
    get_data_dir().mkdir(parents=True, exist_ok=True)
    get_config_dir().mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_dirs()
    app = App()
    app.mainloop()
