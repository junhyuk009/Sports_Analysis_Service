INSERT INTO matches (
    match_id,
    league_id,
    home_team_id,
    away_team_id,
    result,
    score,
    match_datetime,
    status
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (match_id) DO NOTHING;