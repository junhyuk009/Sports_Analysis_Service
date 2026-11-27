
import re
import unicodedata


# --------------------------------------------------
# 1. 선수 이름 정규화
# --------------------------------------------------

def normalize_player_name(name):

    if not name:
        return ""

    name = str(name).strip().lower()

    # 악센트 제거
    name = unicodedata.normalize("NFKD", name)

    name = "".join(
        char for char in name
        if not unicodedata.combining(char)
    )

    # 공백과 특수문자 제거
    name = re.sub(
        r"[^a-z0-9]",
        "",
        name
    )

    return name


# --------------------------------------------------
# 2. 팀별 선수 매칭
# --------------------------------------------------

def match_team_players(csv_players, api_players, team_id):

    results = []

    if not team_id:
        raise ValueError("매칭에 사용할 team_id가 없습니다.")

    for csv_player in csv_players:

        csv_id = csv_player["id"]
        csv_name = csv_player["player_en"]

        normalized_csv_name = normalize_player_name(
            csv_name
        )

        candidates = {}

        # API 선수 목록 비교
        for api_player in api_players:

            api_name = api_player.get("name")
            api_team_id = api_player.get("teamId")
            api_id = api_player.get("id") ###

            if not api_name or api_id is None:
                continue

            # API 팀 ID 확인
            if str(api_team_id) != str(team_id):
                continue

            # 선수 이름 정규화
            normalized_api_name = normalize_player_name(
                api_name
            )

            # 정확히 일치하는 선수만 선택
            if normalized_csv_name != normalized_api_name:
                continue

            # API 선수 ID 기준 중복 제거
            candidates[str(api_id)] = api_player

        # ------------------------------------------
        # 매칭 결과 생성
        # ------------------------------------------

        if len(candidates) == 1:

            api_player = list(candidates.values())[0]

            result = {
                "csv_id": csv_id,
                "csv_player": csv_name,
                "team_id": str(team_id),
                "api_player_id": str(
                    api_player["id"]
                ),
                "api_player_name": api_player["name"],
                "goals": api_player["goals"],
                "assists": api_player["assists"],
                "image_url": api_player.get("image"),
                "match_status": "matched"
            }

        elif len(candidates) > 1:

            result = {
                "csv_id": csv_id,
                "csv_player": csv_name,
                "team_id": str(team_id),
                "api_player_id": None,
                "api_player_name": None,
                "goals": None,
                "assists": None,
                "image_url": None,
                "match_status": "review"
            }

        else:

            result = {
                "csv_id": csv_id,
                "csv_player": csv_name,
                "team_id": str(team_id),
                "api_player_id": None,
                "api_player_name": None,
                "goals": None,
                "assists": None,
                "image_url": None,
                "match_status": "not_found"
            }

        results.append(result)

    return results
