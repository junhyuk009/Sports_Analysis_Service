
from collections import defaultdict, Counter

import psycopg

from backend.database.db import DATABASE_URL, SQL_DIR
from backend.api.player_api import get_team_players
from backend.logic.player_matching import match_team_players


# --------------------------------------------------
# 1. SQL 파일 읽기
# --------------------------------------------------

def load_sql(filename):

    sql_path = SQL_DIR / filename

    if not sql_path.exists():
        raise FileNotFoundError(
            f"SQL 파일을 찾을 수 없습니다: {sql_path}"
        )

    with open(
        sql_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# --------------------------------------------------
# 2. DB 선수 조회
# --------------------------------------------------

def get_db_players():

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL을 확인해주세요.")

    sql = load_sql(
        "select_players_for_matching.sql"
    )

    with psycopg.connect(DATABASE_URL) as conn:

        rows = conn.execute(sql).fetchall()

    players = []

    for row in rows:

        players.append({
            "id": row[0],
            "team": row[1],
            "player_en": row[2],
            "team_id": row[3]
        })

    return players


# --------------------------------------------------
# 3. 팀 ID별 선수 그룹화
# --------------------------------------------------

def group_players_by_team(players):

    team_groups = defaultdict(list)

    no_team_id_players = []

    for player in players:

        team_id = player["team_id"]

        if not team_id:
            no_team_id_players.append(player)
            continue

        team_groups[str(team_id)].append(player)

    return team_groups, no_team_id_players


# --------------------------------------------------
# 4. 팀별 API 조회 및 선수 매칭
# --------------------------------------------------

def match_all_players(team_groups):

    all_results = []

    api_error_teams = []

    total_teams = len(team_groups)

    for index, (team_id, team_players) in enumerate(
        team_groups.items(),
        start=1
    ):

        team_name = team_players[0]["team"]

        print("\n====================================")
        print(f"[{index}/{total_teams}] 팀: {team_name}")
        print(f"팀 ID: {team_id}")
        print(f"DB 선수 수: {len(team_players)}명")

        try:

            # 특정 팀의 선수 목록 조회
            api_players = get_team_players(team_id)

            print(
                f"Goal API 선수 수: {len(api_players)}명"
            )

            # DB 선수와 API 선수 비교
            team_results = match_team_players(
                team_players,
                api_players,
                team_id
            )

            all_results.extend(team_results)

            # 팀별 결과 출력
            for result in team_results:

                print(
                    f"{result['csv_player']} "
                    f"→ {result['match_status']}"
                )

                if result["match_status"] == "matched":

                    print(
                        "   API 선수 이름:",
                        result["api_player_name"]
                    )

                    print(
                        "   API 선수 ID:",
                        result["api_player_id"]
                    )

                    print(
                        "   goals:",
                        result["goals"]
                    )

                    print(
                        "   assists:",
                        result["assists"]
                    )

                    print(
                        "   이미지:",
                        result["image_url"]
                    )

        except Exception as e:

            print(f"팀 API 조회 오류: {e}")

            # API 오류는 not_found로 처리하지 않음
            api_error_teams.append({
                "team": team_name,
                "team_id": team_id,
                "error": str(e)
            })

    return all_results, api_error_teams


# --------------------------------------------------
# 5. 매칭 결과 통계
# --------------------------------------------------

def print_matching_summary(
    all_results,
    no_team_id_players,
    api_error_teams
):

    counts = Counter(
        result["match_status"]
        for result in all_results
    )

    print("\n====================================")
    print("최종 매칭 통계")
    print("====================================")

    print(f"매칭 검사 선수: {len(all_results)}명")
    print(f"matched: {counts['matched']}명")
    print(f"review: {counts['review']}명")
    print(f"not_found: {counts['not_found']}명")
    print(f"team_id 없음: {len(no_team_id_players)}명")
    print(f"API 조회 오류 팀: {len(api_error_teams)}개")


# --------------------------------------------------
# 6. 매칭 선수 DB 저장
# --------------------------------------------------

def save_matched_players(matched_results):

    if not matched_results:
        print("\n저장할 선수가 없습니다.")
        return

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL을 확인해주세요.")

    # API ID 중복 확인
    api_ids = [
        result["api_player_id"]
        for result in matched_results
    ]

    if len(api_ids) != len(set(api_ids)):
        raise ValueError(
            "매칭 결과에 중복된 API 선수 ID가 있습니다."
        )

    # UPDATE SQL 읽기
    sql = load_sql(
        "update_player_api_info.sql"
    )

    save_count = 0

    # 트랜잭션: 오류 발생 시 전체 롤백
    with psycopg.connect(DATABASE_URL) as conn:

        for result in matched_results:

            params = (
                result["api_player_id"],
                result["api_player_name"],
                result["goals"],
                result["assists"],
                result["image_url"],
                result["match_status"],
                result["csv_id"],
                result["team_id"]
            )

            cursor = conn.execute(
                sql,
                params
            )

            if cursor.rowcount != 1:

                raise ValueError(
                    "선수 UPDATE 실패: "
                    f"players.id={result['csv_id']}"
                )

            save_count += 1

    print("\n====================================")
    print("DB 저장 완료")
    print("====================================")
    print(f"저장된 선수: {save_count}명")


# --------------------------------------------------
# 7. 전체 실행
# --------------------------------------------------

def main():

    print("\n===== 1. DB 선수 조회 =====")

    db_players = get_db_players()

    print(f"DB 선수 전체: {len(db_players)}명")

    print("\n===== 2. 팀 ID별 선수 그룹화 =====")

    team_groups, no_team_id_players = (
        group_players_by_team(db_players)
    )

    print(f"조회할 팀 수: {len(team_groups)}개")

    print("\n===== 3. Goal API 팀별 선수 조회 및 매칭 =====")

    all_results, api_error_teams = match_all_players(
        team_groups
    )

    print("\n===== 4. 매칭 통계 =====")

    print_matching_summary(
        all_results,
        no_team_id_players,
        api_error_teams
    )

    # API 오류가 발생한 팀이 있으면 전체 저장 중단
    # 조회하지 못한 팀의 선수 정보가 잘못 처리되는 것을 방지
    if api_error_teams:

        print("\nAPI 조회 오류 팀이 있어 DB 저장을 중단합니다.")

        for team in api_error_teams:
            print(
                team["team"],
                team["error"]
            )

        return

    # matched 결과만 추출
    matched_results = [
        result
        for result in all_results
        if result["match_status"] == "matched"
    ]

    print("\n===== 5. 매칭 성공 선수 DB 저장 =====")

    save_matched_players(matched_results)

    print("\n===== 전체 작업 종료 =====")


if __name__ == "__main__":
    main()
