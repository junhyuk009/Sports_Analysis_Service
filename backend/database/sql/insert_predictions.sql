INSERT INTO predictions (
    user_id,
    match_external_id,
    league_external_id,
    home_team_name,
    away_team_name,
    match_datetime,
    season,
    predicted_result
)

VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s
);