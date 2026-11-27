INSERT INTO users(
    username,
    nickname,
    password_hash
)
VALUES (
    %s, %s, %s
);