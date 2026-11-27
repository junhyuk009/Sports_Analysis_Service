-- 선수 및 팀 ID 조회
--DB에 저장된 선수 이름과 팀 ID를 가져오는 SQL
SELECT
    id,
    team,
    player_en,
    team_id
FROM players
ORDER BY team_id NULLS LAST, id;
