# Köhnə kod (açar birbaşa kodun içindədir)
# api_key = os.environ.get("GEMINI_API_KEY")

# Yeni kod (_api.py-dan oxunur)
from _api import API_KEYS

api_key = API_KEYS.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY 'api.json' faylında tapılmadı.")