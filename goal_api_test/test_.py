
import os
import requests

from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOAL_API_KEY")
BASE_URL = "https://api.goal-api.com/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

KST = ZoneInfo("Asia/Seoul")


def get_matches_by_date(date):
    """특정 날짜의 경기 일정 조회"""

    url = f"{BASE_URL}/fixtures/date/{date}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    result = response.json()

    print(f"\nAPI 응답 성공: {date}")
    print("조회된 경기 수:", result.get("count"))
    print("페이지 정보:", result.get("pagination"))

    return result.get("data", [])


def print_matches(date, matches):
    """경기 일정 출력"""

    print("\n" + "=" * 65)
    print(f"경기 일정: {date}")
    print(f"총 경기 수: {len(matches)}")
    print("=" * 65)

    if not matches:
        print("등록된 경기가 없습니다.")
        return

    # 경기 시작 시간순 정렬
    matches.sort(key=lambda x: x.get("kickoffUtc") or "")

    for match in matches:
        kickoff = match.get("kickoffUtc")

        if kickoff:
            kickoff_time = datetime.fromisoformat(
                kickoff.replace("Z", "+00:00")
            ).astimezone(KST)

            match_date = kickoff_time.strftime("%Y-%m-%d")
            match_time = kickoff_time.strftime("%H:%M")
        else:
            match_date = "날짜 정보 없음"
            match_time = "시간 정보 없음"

        league = match.get("league", {}).get("name", "리그 정보 없음")
        home = match.get("homeTeam", {}).get("name", "홈팀 정보 없음")
        away = match.get("awayTeam", {}).get("name", "원정팀 정보 없음")
        status = match.get("matchStatus", "상태 정보 없음")

        print("-" * 65)
        print(f"리그: {league}")
        print(f"경기: {home} vs {away}")
        print(f"날짜: {match_date}")
        print(f"시간: {match_time} (한국 시간)")
        print(f"상태: {status}")


def main():
    if not API_KEY:
        raise ValueError("GOAL_API_KEY를 확인해주세요.")

    today = datetime.now(KST).date()

    dates = [
        today.strftime("%Y-%m-%d"),
        today.replace(day=today.day).strftime("%Y-%m-%d")
    ]

    # 내일 날짜 추가
    from datetime import timedelta
    tomorrow = today + timedelta(days=1)
    dates[1] = tomorrow.strftime("%Y-%m-%d")

    for date in dates:
        matches = get_matches_by_date(date)
        print_matches(date, matches)


if __name__ == "__main__":
    main()
