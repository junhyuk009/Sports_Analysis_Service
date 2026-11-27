-- 프리미어 리그 팀 테이블
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    team_id VARCHAR(100) NOT NULL UNIQUE, -- 팀 아이디
    team_name_en VARCHAR(100) NOT NULL, -- 팀 이름(영문)
    team_name_ko VARCHAR(100), -- 팀 이름 (수기 입력)

    image TEXT -- 팀 로고URL
);
