# api에서 팀데이터를 가져와 teams테이블에 저장
from backend.api.team_api import get_premier_league_teams
from backend.database.db import save_teams


def update_teams():
    # API에서 팀 데이터 가져오기
    teams = get_premier_league_teams()

    if not teams:
        print("조회된 팀이 없습니다.")
        return

    print(f"API에서 팀 데이터 {len(teams)}개 조회 완료!")

    # DB에 팀 정보 저장하기
    save_teams(teams)


if __name__ == "__main__":
    update_teams()
