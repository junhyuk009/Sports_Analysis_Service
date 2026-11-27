
-- 포인트 지급 내역 테이블
CREATE TABLE IF NOT EXISTS point_history (
    point_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,
    prediction_id UUID NOT NULL,

    -- 지급 포인트
    amount INTEGER NOT NULL DEFAULT 10,

    -- 지급 사유
    reason VARCHAR(100) NOT NULL DEFAULT '경기 예측 정답',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 사용자 FK
    CONSTRAINT fk_point_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT,

    -- 예측 FK
    CONSTRAINT fk_point_prediction
        FOREIGN KEY (prediction_id)
        REFERENCES predictions(prediction_id)
        ON DELETE RESTRICT,

    -- 지급 포인트는 양수만 허용
    CONSTRAINT chk_point_amount
        CHECK (amount > 0),

    -- 동일 예측에 중복 지급 방지
    CONSTRAINT uq_point_prediction
        UNIQUE (prediction_id)
);
