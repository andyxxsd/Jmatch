-- DROP DATABASE IF EXISTS Jmatch;
-- CREATE DATABASE Jmatch;
-- USE Jmatch;

DROP TABLE IF EXISTS users;
CREATE TABLE users(
	id INTEGER PRIMARY KEY,
	name TEXT
);

DROP TABLE IF EXISTS games;
CREATE TABLE games(
	id INTEGER PRIMARY KEY,
	name TEXT,
	playersNumber INTEGER
);

DROP TABLE IF EXISTS matches;
CREATE TABLE matches(
	mid INTEGER PRIMARY KEY,
	winner INTEGER,
	loser INTEGER,
	FOREIGN KEY (winner) REFERENCES users(id),
	FOREIGN KEY (loser) REFERENCES users(id)
);

--Using left join to make sure users without matches will appear on standing
--Temp table A is used for counting win matches
--Temp table B is used for counting total matches
DROP VIEW IF EXISTS playerStandings;
CREATE VIEW playerStandings AS
SELECT P.id, P.name, count(A.winner) wins, count(B.winner) matches
FROM users P, (users LEFT JOIN matches ON users.id = matches.winner) A,
	(users LEFT JOIN matches ON users.id = matches.winner OR users.id = matches.loser) B
WHERE P.id = A.id AND P.id = B.id
GROUP BY P.id
ORDER BY wins;
