-- predictions: 경기 시작 전 사용자의 예측 변경
-- 전제: predictions.match_external_id = matches.match_id
-- 파라미터 순서: (predicted_result, user_id, match_external_id)
-- 경기 시작 시각에 도달했거나 정산된 예측은 변경하지 않습니다.

UPDATE predictions AS p
SET predicted_result = %s
FROM matches AS m
WHERE p.user_id = %s
  AND p.match_external_id = %s
  AND m.match_id = p.match_external_id
  AND m.match_datetime > CURRENT_TIMESTAMP
  AND p.is_settled = FALSE;
