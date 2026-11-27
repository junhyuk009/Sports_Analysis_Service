--api에서 선수 정보를 받아와 업데이트
UPDATE players
SET
    api_player_id = %s,
    api_player_name = %s,
    goals = %s,
    assists = %s,
    image_url = %s,
    match_status = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE id = %s
  AND team_id = %s;