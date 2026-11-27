UPDATE players p
SET team_id = t.team_id
FROM teams t
WHERE p.team = t.team_name_en
  AND p.team_id IS DISTINCT FROM t.team_id;

-- teams 테이블 team_id >> players 테이블에 저장 (팀 이름 조회 및 대조)