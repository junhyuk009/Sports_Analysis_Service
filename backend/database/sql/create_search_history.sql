CREATE TABLE IF NOT EXISTS search_history ( -- gpt 질의응답
    search_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
--         ON DELETE CASCADE, -- 부모테이블에서 데이터 삭제 시, 해당되는 데이터 삭제
    question TEXT NOT NULL, -- 질문
    answer TEXT NOT NULL, -- 응답
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- 생성일자 (질문 시간)
);