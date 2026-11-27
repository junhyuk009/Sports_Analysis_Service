-- predictions: 경기 종료 후 실제 결과 및 예측 정산 정보 저장
-- 파라미터 순서: (actual_result, is_correct, points_earned, prediction_id)
-- 포인트 적립 이력은 별도의 insert_point_history.sql로 처리합니다.

UPDATE predictions
SET
    actual_result = %s,
    is_correct = %s,
    points_earned = %s,
    is_settled = TRUE,
    settled_at = CURRENT_TIMESTAMP
WHERE prediction_id = %s
  AND is_settled = FALSE;
