
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# 1. 환경 설정
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")

API_KEY = os.getenv("GOAL_API_KEY")
GOAL_API_URL = os.getenv("GOAL_API_URL")


# --------------------------------------------------
# 2. API 인증 헤더
# --------------------------------------------------

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}


# --------------------------------------------------
# 3. API 설정 확인
# --------------------------------------------------

def check_api_settings():

    if not API_KEY:
        raise ValueError("GOAL_API_KEY가 없습니다.")

    if not GOAL_API_URL:
        raise ValueError("GOAL_API_URL이 없습니다.")


# --------------------------------------------------
# 4. 특정 팀의 선수 목록 조회
# --------------------------------------------------

def get_team_players(team_id):

    check_api_settings()

    if not team_id:
        raise ValueError("team_id가 없습니다.")

    url = f"{GOAL_API_URL}/teams/{team_id}/players"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise ValueError(
            f"Goal API 선수 조회 실패: {result}"
        )

    players = result.get("data", [])

    if not isinstance(players, list):
        raise ValueError(
            "API 선수 데이터 형식이 올바르지 않습니다."
        )

    return players


# --------------------------------------------------
# 5. 직접 실행 테스트
# --------------------------------------------------

if __name__ == "__main__":

    print("===== Goal API 팀 선수 조회 테스트 =====")

    try:

        team_id = input(
            "Goal API team_id 입력: "
        ).strip()

        players = get_team_players(team_id)

        print(f"\n조회된 선수 수: {len(players)}명")

        for player in players:

            print("----------------------------")
            print("API 선수 ID:", player.get("id"))
            print("goals:", player.get("goals"))
            print("assists:", player.get("assists"))
            print("선수 이름:", player.get("name"))
            print("팀 ID:", player.get("teamId"))
            print("이미지 URL:", player.get("image"))

    except Exception as e:

        print("API 조회 오류:", e)
