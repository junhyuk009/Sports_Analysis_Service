-- dubbing: 더빙 완료 결과 URL 저장 및 상태 변경
-- 파라미터 순서: (result_url, dubbing_id)

UPDATE dubbing
SET
    result_url = %s,
    status = 'Y'
WHERE dubbing_id = %s;
