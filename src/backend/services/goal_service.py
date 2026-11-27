# goal_service.py
# GOAL API

import httpx
from fastapi import HTTPException
from src.backend.core.config import (
    GOAL_API_KEY,
    GOAL_BASE_URL,
    GOAL_HEADERS
)
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 외부 HTTP 비동기 클라이언트 생성
def make_client(timeout: float = 60.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout, follow_redirects=False)

# 외부 응답의 JSON 본문과 HTTP 오류를 일관되게 처리
# 일부 오류가 JSON이 아닐 수 있으므로 문자열로도 안전하게 처리
def parse_response(response: httpx.Response) -> dict:
    try:
        data = response.json() if response.content else {}
    except ValueError:
        data = {'message': response.text[:120]}
    if response.status_code >= 400:
        err = data if isinstance(data, dict) else {'message': str(data)}
        raise HTTPException(
            status_code=response.status_code,
            detail={
                'code': err.get('code', ''),
                'detailCode': err.get('detailCode', ''),
                'message': err.get('message', err.get('detail',
                                                    '외부 routers 오류')),
            },
        )
    if not isinstance(data, dict):
        raise HTTPException(502, '예상하지 못한 Perso 응답 형식')
    return data

# goal api 서버에 KEY 헤더를 붙여 실제 HTTP 요청 전송
async def goal_call(method: str, path: str, *, params=None, json=None) -> dict:
    if not GOAL_API_KEY:
        raise HTTPException(503, 'GOAL_API_KEY 환경 변수가 없습니다')
    try:
        async with make_client() as client:
            response = await client.request(
                method, GOAL_BASE_URL + path, params=params, json=json,
                headers=GOAL_HEADERS
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(504, 'Goal API 요청 시간 초과') from exc
    except httpx.RequestError as exc:
        raise HTTPException(502, 'Goal API 연결 오류') from exc
    return parse_response(response)

# 리그 가져오기
async def get_league():
    result = await goal_call(
        'GET',
        '/leagues'
    )
    return result.get('data', [])

# EPL 팀 목록()
async def get_epl():
    leagues = await get_league()

    epl_id = None

    for league in leagues:
        if league.get('name') == 'Premier League' and league.get('countryName') == 'England':
            epl_id = league.get('id')
            break

    if epl_id is None:
        raise HTTPException(404, '해당 리그를 찾을 수 없습니다')

    result = await goal_call(
        'GET',
        f'/leagues/{epl_id}/teams'
    )

    return result.get('data', [])

# 득점 상위 5명 출력
async def top_scorer():
    leagues = await get_league()

    epl_id = None

    for league in leagues:
        if league.get('name') == 'Premier League' and league.get('countryName') == 'England':
            epl_id = league.get('id')
            break

    if epl_id is None:
        raise HTTPException(404, '해당 리그를 찾을 수 없습니다')

    result = await goal_call(
        'GET',
        f'/leagues/{epl_id}/top-scorers'
    )

    return result.get('data', [])[:5]

# 리그 순위 / 승점
async def rank_team():
    leagues = await get_league()

    epl_id = None

    for league in leagues:
        if league.get('name') == 'Premier League' and league.get('countryName') == 'England':
            epl_id = league.get('id')
            break

    if epl_id is None:
        raise HTTPException(404, '해당 리그를 찾을 수 없습니다')

    result = await goal_call(
        'GET',
        f'/standings/{epl_id}'
    )

    return result.get('data', [])

# 팀 스쿼드
async def team_players(team_id: str):
    result = await goal_call(
        'GET',
        f'/teams/{team_id}/players'
    )
    return result.get('data', [])


# 선수 검색(일단 만들어둠)
async def search_player(name: str):
    result = await goal_call(
        'GET',
        f'/players/search?q={name}'
    )

    players = result.get('data', [])

    for player in players:
        if player['name'] == name:
            return player
        break


# 경기 당일 기준 앞뒤로 EPL 전체 팀 7일 일정 조회 (시간 KST 변환)
async def team_fixtures():
    recent_matches = []
    match_ids = set()

    data = await get_epl()

    # EPL 리그 ID
    epl_id = 'cmr77dvkr005nrx06lp7rvp49'

    # 한국 기준 오늘 날짜
    today = datetime.now(ZoneInfo('Asia/Seoul')).date()

    for ids in data:
        team_id = ids.get('id')

        if not team_id:
            continue

        result = await goal_call(
            'GET',
            f'/teams/{team_id}/fixtures'
        )

        matches = result.get('data', [])

        for match in matches:
            # EPL 경기만 필터링
            if match.get('leagueId') != epl_id:
                continue



            match_date = match.get('matchDate')
            match_time = match.get('matchTime')

            if not match_date or not match_time:
                continue

            # 경기 날짜 + 시간 결합
            utc_time = datetime.strptime(
                f"{match_date} {match_time}",
                "%Y-%m-%d %H:%M"
            )

            # UTC → KST 변환
            utc_time = utc_time.replace(tzinfo=ZoneInfo('UTC'))
            kst_time = utc_time.astimezone(ZoneInfo('Asia/Seoul'))

            match['matchDate'] = kst_time.strftime('%Y-%m-%d')
            match['matchTime'] = kst_time.strftime('%H:%M')

            # 오늘 기준 앞뒤 7일
            if today - timedelta(days=7) <= kst_time.date() <= today + timedelta(days=7):
                match_id = match.get('id')

                if match_id and match_id not in match_ids:
                    match_ids.add(match_id)
                    recent_matches.append(match)

    # 모든 경기 조회 후 날짜순 정렬
    recent_matches.sort(
        key=lambda match: (
            match['matchDate'],
            match['matchTime']
        )
    )

    return recent_matches





































































