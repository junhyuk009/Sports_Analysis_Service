INSERT INTO dubbing (
    project_seq,
    media_seq,
    source_url,
    language,
    target_language,
    status
)
VALUES (
    %s, %s, %s, %s, %s, 'N'
);