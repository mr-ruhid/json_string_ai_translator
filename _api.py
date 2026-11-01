# _api.py
import json
import os

API_KEYS_FILE = "api.json"

def load_api_keys():
    """api.json faylından API açarlarını oxuyur."""
    if not os.path.exists(API_KEYS_FILE):
        raise FileNotFoundError(
            f"'{API_KEYS_FILE}' tapılmadı. Zəhmət olmasa layihə qovluğunda yaradın."
        )
    
    with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
        keys = json.load(f)
    
    return keys

# API açarlarını yüklə
try:
    API_KEYS = load_api_keys()
except FileNotFoundError as e:
    print(f"⚠️ Xəbərdarlıq: {e}")
    API_KEYS = {}