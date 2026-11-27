import os
from pathlib import Path
import pandas as pd
import psycopg
from dotenv import load_dotenv


# project2 폴더 경로
ROOT_DIR = Path(__file__).resolve().parents[2]

# project2/.env 불러오기
load_dotenv(ROOT_DIR / ".env")

# DB 접속 주소
DATABASE_URL = os.getenv("DATABASE_URL")

# SQL 파일 폴더
SQL_DIR = Path(__file__).parent / "sql"


def execute_sql(filename):
    """SQL 파일 실행"""

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL을 확인해주세요.")

    sql_path = SQL_DIR / filename

    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(sql)

    print(f"{filename} 실행 완료")


def initialize_db():
    """전체 테이블 생성"""

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL을 확인해주세요.")

    execute_sql("create_users.sql")
    execute_sql("create_teams.sql")
    execute_sql("create_players.sql")
    execute_sql("create_predictions.sql")
    execute_sql("create_point_history.sql")
    execute_sql("create_matches.sql")
    execute_sql("create_dubbing.sql")
    execute_sql("create_search_history.sql")
    execute_sql("create_indexes.sql")

    print("모든 DB 테이블 생성 완료!")


def save_teams(teams):
    """API에서 가져온 팀 정보를 DB에 저장"""

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL을 확인해주세요.")

    if not teams:
        print("저장할 팀 데이터가 없습니다.")
        return

    # 팀 저장 SQL 읽기
    sql_path = SQL_DIR / "insert_teams.sql"

    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    save_count = 0

    # DB 연결 및 팀 데이터 저장
    with psycopg.connect(DATABASE_URL) as conn:

        for team in teams:

            # API 응답에서 팀 정보 가져오기
            team_id = team.get("id")
            team_name_en = team.get("name")
            image = team.get("badge")

            # 필수 데이터 확인
            if not team_id or not team_name_en:
                print(f"팀 데이터 누락으로 저장 제외: {team}")
                continue

            # SQL 실행
            conn.execute(
                sql,
                (
                    str(team_id),
                    team_name_en,
                    image
                )
            )

            save_count += 1
    print(f"팀 데이터 {save_count}개 저장 완료!")

def save_players():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL을 확인해주세요.")

    # CSV 파일 경로
    csv_path = Path(__file__).parent / "epl_players.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

    # CSV 읽기
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # 필요한 컬럼 확인
    required_columns = [
        "id", "team", "team_ko", "player_en", "player_ko",
        "birth_year", "age", "country", "height_cm",
        "number", "position"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"CSV에 '{column}' 컬럼이 없습니다.")


    # SQL 파일 읽기
    sql_path = SQL_DIR / "insert_players.sql"

    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    save_count = 0

    def clean_text(value):
        if pd.isna(value) or str(value).strip() == "":
            return None
        return str(value).strip()

    def clean_int(value):
        if pd.isna(value) or str(value).strip() == "":
            return None
        return int(value)

    with psycopg.connect(DATABASE_URL) as conn:
        for _, row in df.iterrows():

            params = (
                int(row["id"]),
                clean_text(row["team"]),
                clean_text(row["team_ko"]),
                clean_text(row["player_en"]),
                clean_text(row["player_ko"]),
                clean_int(row["birth_year"]),
                clean_int(row["age"]),
                clean_text(row["country"]),
                clean_int(row["height_cm"]),
                clean_int(row["number"]),
                clean_text(row["position"])
            )

            result = conn.execute(sql, params)

            if result.rowcount == 1:
                save_count += 1

    print(f"선수 데이터 {save_count}개 저장 완료!")


if __name__ == "__main__":
    initialize_db()
    save_players()