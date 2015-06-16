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

DROP TABLE IF EXISTS lobby;
CREATE TABLE lobby(
	uid INTEGER NOT NULL,
	gid INTEGER NOT NULL,
	status TEXT NOT NULL,
	PRIMARY KEY(uid),
	FOREIGN KEY (uid) REFERENCES users(id),
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


DROP VIEW IF EXISTS attend;
CREATE VIEW attend AS
select users.id uid, matches.id mid
from users, matches, winners, losers
where (users.id = winners.uid or users.id = losers.uid) and matches.id = winners.mid and matches.id = losers.mid;


DROP VIEW IF EXISTS ranks;
CREATE VIEW ranks AS
select win.id, win.username, win.game, win.wins, tot.matches from
(select U.id, U.username, G.name game, A.wins
from users U, games G, (select users.id id, matches.gid, count(winners.uid) wins
		from users join attend on users.id = attend.uid join matches on matches.id = attend.mid
		left join winners on matches.id = winners.mid and users.id = winners.uid
		group by users.id, matches.gid) A
where U.id = A.id and G.id = A.gid) win,
(select users.id id, users.username username, games.name game, count(matches.id) matches
from users, games, matches, winners, losers
where (users.id = winners.uid or users.id = losers.uid) and games.id = matches.gid and matches.id = winners.mid and matches.id = losers.mid
group by users.id, games.name) tot
where win.id = tot.id and win.game = tot.game
