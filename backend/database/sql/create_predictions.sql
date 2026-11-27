
-- 경기 예측 테이블
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 사용자 ID
    user_id UUID NOT NULL,

    -- Goal API 경기 및 리그 ID
    match_external_id VARCHAR(100) NOT NULL,
    league_external_id VARCHAR(100),

    -- 경기 정보
    home_team_name VARCHAR(100) NOT NULL,
    away_team_name VARCHAR(100) NOT NULL,
    match_datetime TIMESTAMPTZ NOT NULL,
    season VARCHAR(20),

    -- 사용자 예측 결과
    predicted_result VARCHAR(10) NOT NULL,

    -- 실제 경기 결과
    actual_result VARCHAR(10),

    -- 예측 정답 여부
    is_correct BOOLEAN,

    -- 획득 포인트
    points_earned INTEGER NOT NULL DEFAULT 0,

    -- 정산 여부
    is_settled BOOLEAN NOT NULL DEFAULT FALSE,
    settled_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 사용자 FK
    CONSTRAINT fk_predictions_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT,

    -- 예측 결과 제한
    CONSTRAINT chk_predicted_result
        CHECK (
            predicted_result IN ('HOME_WIN', 'DRAW', 'AWAY_WIN')
        ),

    -- 실제 결과 제한
    CONSTRAINT chk_actual_result
        CHECK (
            actual_result IS NULL
            OR actual_result IN ('HOME_WIN', 'DRAW', 'AWAY_WIN')
        ),

    -- 정산 상태 확인
    CONSTRAINT chk_settlement_time
        CHECK (
            (is_settled = FALSE AND settled_at IS NULL)
            OR
            (is_settled = TRUE AND settled_at IS NOT NULL)
        ),

    -- 한 사용자는 한 경기에 한 번만 예측
    CONSTRAINT uq_user_match
        UNIQUE (user_id, match_external_id)
);
