import json
import os

class Config:
    DEFAULT_CONFIG = {
        "username": os.environ.get('USERNAME', 'User'),
        "room_code": "1234",
        "autostart": True
    }
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".lancollab_config.json")

    @classmethod
    def load(cls):
        if os.path.exists(cls.CONFIG_PATH):
            try:
                with open(cls.CONFIG_PATH, "r", encoding="utf-8") as f:
                    return {**cls.DEFAULT_CONFIG, **json.load(f)}
            except Exception:
                return cls.DEFAULT_CONFIG
        return cls.DEFAULT_CONFIG

    @classmethod
    def save(cls, config_data):
        with open(cls.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
