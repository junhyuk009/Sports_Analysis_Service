-- api에서 팀ID, 이름(영문), 로고URL 호출해 create_teams.sql에 추가하기
INSERT INTO teams (
    team_id,
    team_name_en,
    image
)
VALUES (
    %s, %s, %s
)
ON CONFLICT (team_id) --기존 아이디와 동일시
DO UPDATE SET -- 새 데이터로 수정
    team_name_en = EXCLUDED.team_name_en,
    image = EXCLUDED.image;