import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# project2 폴더 경로
ROOT_DIR = Path(__file__).resolve().parents[2]

# project2/.env 파일 불러오기
load_dotenv(ROOT_DIR / ".env")


# 환경변수 가져오기
API_KEY = os.getenv("GOAL_API_KEY")
GOAL_API_URL = os.getenv("GOAL_API_URL")
PREMIER_LEAGUE_ID = os.getenv("PREMIER_LEAGUE_ID")

# API 인증 헤더
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

# 프리미어리그 팀 목록 조회
def get_premier_league_teams():
    # 환경변수 확인
    if not API_KEY:
        raise ValueError("GOAL_API_KEY가 없습니다.")

    if not GOAL_API_URL:
        raise ValueError("GOAL_API_URL이 없습니다.")

    if not PREMIER_LEAGUE_ID:
        raise ValueError("PREMIER_LEAGUE_ID가 없습니다.")

    # API 주소
    url = f"{GOAL_API_URL}/leagues/{PREMIER_LEAGUE_ID}/teams"

    # API 요청
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()

    result = response.json()

    return result.get("data", [])

