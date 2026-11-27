-- users: 사용자의 응원팀 변경
UPDATE users
SET my_team_external_id = %s
WHERE user_id = %s;
