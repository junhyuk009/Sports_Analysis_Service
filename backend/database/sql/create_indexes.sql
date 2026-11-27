
-- 사용자별 최신 예측 조회
CREATE INDEX IF NOT EXISTS idx_predictions_user_date
ON predictions (user_id, created_at DESC);


-- 미정산 경기 조회
CREATE INDEX IF NOT EXISTS idx_predictions_unsettled
ON predictions (is_settled, match_datetime);


-- 사용자별 포인트 내역 조회
CREATE INDEX IF NOT EXISTS idx_point_history_user_date
ON point_history (user_id, created_at DESC);
