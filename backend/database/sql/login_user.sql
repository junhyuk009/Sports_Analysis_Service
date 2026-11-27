SELECT
    user_id,
    username,
    nickname,
    password_hash
FROM users
WHERE username = %s;