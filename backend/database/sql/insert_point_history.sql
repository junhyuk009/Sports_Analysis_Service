INSERT INTO point_history (
    user_id,
    prediction_id,
    amount,
    reason
)
VALUES (
    %s, %s, %s, %s
)
ON CONFLICT (prediction_id) DO NOTHING;