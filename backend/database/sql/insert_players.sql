INSERT INTO players (
    id,
    team,
    team_ko,
    player_en,
    player_ko,
    birth_year,
    age,
    country,
    height_cm,
    number,
    position
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO NOTHING;