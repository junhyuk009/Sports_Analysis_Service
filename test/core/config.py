import os
from dotenv import load_dotenv

load_dotenv()

PERSO_BASE_URL = "https://api.perso.ai"
PERSO_MEDIA_URL = "https://portal-media.perso.ai"
PERSO_API_KEY = os.getenv("PERSO_API_KEY")
PERSO_SPACE_SEQ = int(os.getenv("PERSO_SPACE_SEQ", "0"))
GOAL_API_KEY = os.getenv('AI_API_KEY', '').strip()
GOAL_BASE_URL = "https://api.goal-api.com/v1"
GOAL_HEADERS = {"Authorization": f"Bearer {GOAL_API_KEY}"}
