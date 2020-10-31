SELECT User.id, Score.score, Score.streak 
FROM User JOIN Score ON User.id = Score.user_id
WHERE User.nick = ? AND Score.server_id = ?;