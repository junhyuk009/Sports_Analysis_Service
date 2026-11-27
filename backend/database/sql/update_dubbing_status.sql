-- dubbing: 더빙 작업 상태 변경
-- 파라미터 순서: (status, dubbing_id)

UPDATE dubbing
SET status = %s
WHERE dubbing_id = %s;
