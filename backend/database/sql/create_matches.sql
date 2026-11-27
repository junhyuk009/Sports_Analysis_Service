CREATE TABLE IF NOT EXISTS matches ( -- 경기 기록
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id VARCHAR(100) NOT NULL UNIQUE, -- 경기 매치 ID
    league_id VARCHAR(100), -- 리그 ID
    home_team_id VARCHAR(100), -- 홈팀 ID
--         REFERENCES teams(team_id), --team_id 테이블 참조
    away_team_id VARCHAR(100),
--         REFERENCES teams(team_id),
    result VARCHAR(10), -- 경기 결과 승/무/패
    score VARCHAR(20), -- 경기 점수
    match_datetime TIMESTAMPTZ NOT NULL, -- 경기 날짜
    status VARCHAR(30), -- 경기 상태 예정/라이브/종료
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- 데이터 생성 일자
);