from functools import lru_cache
import requests
import yt_dlp
import streamlit as st
import os
from dotenv import load_dotenv
from googlenewsdecoder import gnewsdecoder # 뉴스 기사 주소 디코딩


load_dotenv()

# 1. Goal routers 키 입력
GOAL_API_KEY = os.getenv('AI_API_KEY', '').strip()
GOAL_BASE_URL = "https://api.goal-api.com/v1"
GOAL_HEADERS = {"Authorization": f"Bearer {GOAL_API_KEY}"}

@lru_cache(maxsize=1)
def get_current_pl_teams():
    """[Goal routers] 이번 시즌 프리미어리그 20개 팀 목록 동적 추출 (승격/강등 자동 반영)"""
    # 프리미어리그 ID 찾기
    l_res = requests.get(f"{GOAL_BASE_URL}/leagues", headers=GOAL_HEADERS, params={"search": "Premier League"})
    pl_id = None
    for lg in l_res.json().get("data", []):
        if lg.get("countryName") == "England":
            pl_id = lg.get("id")
            break

    if not pl_id:
        return []

    # 순위표에서 이번 시즌 20개 팀 이름 추출
    standings_res = requests.get(f"{GOAL_BASE_URL}/standings/{pl_id}", headers=GOAL_HEADERS)
    teams = []
    if standings_res.status_code == 200:
        for row in standings_res.json().get("data", []):
            teams.append(row.get("teamName"))
    return teams

def get_match_highlights(home_team, away_team, match_date, count=5):
    query = f"{home_team} vs {away_team} {match_date} highlights"

    options = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "noplaylist": True
    }

    videos = []

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            result = ydl.extract_info(
                f"ytsearch{count}:{query}",
                download=False
            )

        for video in result.get("entries", []):
            if not video or not video.get("id"):
                continue

            videos.append({
                "title": video.get("title"),
                "channel": video.get("channel"),
                "url": f"https://www.youtube.com/watch?v={video['id']}"
            })

    except Exception as e:
        print("영상 검색 실패:", e)

    return videos

# 예시
st.title('하이라이트 검색')

pl_teams = get_current_pl_teams()

home_team = st.selectbox('홈팀 선택', pl_teams)
away_team = st.selectbox('원정팀 선택', pl_teams)
match_date = st.date_input('경기 날짜 선택')

st.subheader(f"{home_team} vs {away_team}")

if st.button("경기 하이라이트 검색"):
    st.session_state.videos = get_match_highlights(
        home_team,
        away_team,
        match_date
    )
if "videos" in st.session_state:
    videos = st.session_state.videos
    if videos:
        selected_video = st.selectbox(
            "하이라이트 선택",
            videos,
            format_func=lambda v: v["title"]
        )
        print(selected_video)
        st.write("채널:", selected_video["channel"])
        st.video('https://portal-media.perso.ai/perso-storage/68c4b687-f56c-46ce-95f3-1926b41219bb/2026_11/p-451858/Soccer_Highlight_ENtoKO_TranslatedVideo_1795652579832.mp4')
        print(selected_video["url"])
    else:
        st.warning("검색된 하이라이트가 없습니다.")

