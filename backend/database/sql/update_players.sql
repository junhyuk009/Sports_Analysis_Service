UPDATE players
SET
    team_id = %s,
    api_player_id = %s,
    api_player_name = %s,
    goals = %s
    assists = %s
    image_url = %s,
    match_status = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE id = %s;
