-- DROP DATABASE IF EXISTS Jmatch;
-- CREATE DATABASE Jmatch;
-- USE Jmatch;

DROP TABLE IF EXISTS users;
CREATE TABLE users(
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	accesstoken TEXT NOT NULL,
	nickname TEXT
);

DROP TABLE IF EXISTS games;
CREATE TABLE games(
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE NOT NULL,
	playersNumber INTEGER
);

DROP TABLE IF EXISTS matches;
CREATE TABLE matches(
	id INTEGER PRIMARY KEY,
	gid INTEGER NOT NULL,
	createdTime INTEGER NOT NULL,
	FOREIGN KEY (gid) REFERENCES games(id)
);

DROP TABLE IF EXISTS winners;
CREATE TABLE winners(
	mid INTEGER NOT NULL,
	uid INTEGER NOT NULL,
	PRIMARY KEY(mid, uid),
	FOREIGN KEY (mid) REFERENCES matches(id),
	FOREIGN KEY (uid) REFERENCES users(id)
);

DROP TABLE IF EXISTS losers;
CREATE TABLE losers(
	mid INTEGER NOT NULL,
	uid INTEGER NOT NULL,
	PRIMARY KEY(mid, uid),
	FOREIGN KEY (mid) REFERENCES matches(id),
	FOREIGN KEY (uid) REFERENCES users(id)
);

DROP TABLE IF EXISTS roles;
CREATE TABLE roles(
	id INTEGER PRIMARY KEY,
	uid INTEGER NOT NULL,
	access TEXT NOT NULL,
	FOREIGN KEY (uid) REFERENCES users(id)
);

INSERT INTO users (id, username, password, accesstoken) values(1024, "admin", "yaya", "thisIsAnAccesstoken");
INSERT INTO roles (uid, access) values(1024, "admin");

--Using left join to make sure users without matches will appear on standing
--Temp table A is used for counting win matches
--Temp table B is used for counting total matches
-- DROP VIEW IF EXISTS playerStandings;
-- CREATE VIEW playerStandings AS
-- SELECT P.id, P.name, count(A.winner) wins, count(B.winner) matches
-- FROM users P, (users LEFT JOIN matches ON users.id = matches.winner) A,
-- 	(users LEFT JOIN matches ON users.id = matches.winner OR users.id = matches.loser) B
-- WHERE P.id = A.id AND P.id = B.id
-- GROUP BY P.id
-- ORDER BY wins;
