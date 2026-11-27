CREATE TABLE IF NOT EXISTS dubbing ( --perso api를 위한 원본 url DB 저장
    dubbing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_seq VARCHAR(100), -- 프로젝트 ID
    media_seq VARCHAR(100),
    source_url TEXT NOT NULL, -- api로 호출한 원본영상 url
    result_url TEXT, -- 더빙 완료 영상
    language VARCHAR(20), -- 원본 언어
    target_language VARCHAR(20), -- 번역 언어
    status VARCHAR(20) DEFAULT 'N' -- 작업 상태 여부
        CHECK (status IN (
            'Y',
            'N'
        )),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- 생성 일자
);