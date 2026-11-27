-- EPL 선수 테이블 생성
CREATE TABLE IF NOT EXISTS players (

    -- 우리 프로젝트 내부 선수 ID
    id INTEGER PRIMARY KEY,

    -- CSV 선수 기본 정보
    team VARCHAR(100) NOT NULL,
    team_ko VARCHAR(100),
    player_en VARCHAR(150) NOT NULL,
    player_ko VARCHAR(150),

    birth_year INTEGER,
    age INTEGER,
    country VARCHAR(100),
    height_cm INTEGER,
    number INTEGER,
    position VARCHAR(20),

    -- 외부 축구 API 연결 정보
    team_id VARCHAR(100),
    api_player_id VARCHAR(100) UNIQUE,
    api_player_name VARCHAR(150),
    goals VARCHAR(20),
    assists VARCHAR(20),
    image_url TEXT,

    -- API 선수 매칭 상태
    match_status VARCHAR(20) DEFAULT 'pending',

    -- 데이터 등록 및 수정 시간
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
