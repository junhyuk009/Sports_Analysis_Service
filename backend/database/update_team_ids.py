# teams 테이블 team_id >> players 테이블에 저장
import psycopg
from backend.database.db import DATABASE_URL, SQL_DIR


def update_player_team_ids():

    sql_path = SQL_DIR / "update_player_team_ids.sql"

    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

            print(f"team_id 업데이트 완료: {cur.rowcount}명")


if __name__ == "__main__":
    update_player_team_ids()
