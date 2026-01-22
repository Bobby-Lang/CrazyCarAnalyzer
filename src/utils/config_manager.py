import json
import os
from src.utils.paths import get_config_dir
from src.utils.encryption import encrypt_password, decrypt_password

class ConfigManager:
    _instance = None
    
    DEFAULT_CONFIG = {
        "accounts": [],  # List of {phone, password, last_used}
        "current_account_idx": -1,
        "substitution_map": {
            "新手o↘.ヾ": "十郎",
            "新手o↘.": "凌霄",
            "幻紫高达战队": "幻紫高达",
            "炫金高达战队": "炫金高达"
        },
        "custom_pages": [
            { "name": "第一阶段", "start_map": "绿色山谷", "end_map": "雪邦" },
            { "name": "第二阶段", "start_map": "决战山脊", "end_map": "" }
        ],
        "game_settings": {
            "mode": "组队竞速",
            "start_maps": ["绿色山谷"],
            "end_map": ""
        },
        "app_settings": {
            "auto_open_report": True,
            "theme": "Dark"
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.config_path = get_config_dir() / "user_config.json"
            cls._instance.config = cls._instance.load_config()
        return cls._instance

    def load_config(self):
        if not self.config_path.exists():
            return self.DEFAULT_CONFIG.copy()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        # Ensure dir exists
        if not self.config_path.parent.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def get_current_account(self):
        idx = self.config.get("current_account_idx", -1)
        accounts = self.config.get("accounts", [])
        if 0 <= idx < len(accounts):
            acc = accounts[idx].copy()
            acc["password"] = decrypt_password(acc.get("password", ""))
            return acc
        return None

    def add_or_update_account(self, phone, password):
        accounts = self.config.get("accounts", [])
        enc_pwd = encrypt_password(password)
        
        # Check if exists
        for i, acc in enumerate(accounts):
            if acc["phone"] == phone:
                accounts[i]["password"] = enc_pwd
                self.config["current_account_idx"] = i
                self.save_config()
                return

        # Add new
        accounts.append({"phone": phone, "password": enc_pwd})
        self.config["accounts"] = accounts
        self.config["current_account_idx"] = len(accounts) - 1
        self.save_config()

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
