# 我的锅游戏匹配平台(Jmatch) Scheme Documentation
#### use SQLite3, database file in the root directory

##用户
####users
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	accesstoken TEXT NOT NULL,
	nickname TEXT


##游戏
####games
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE NOT NULL,
	playersNumber INTEGER


##对局
####matches
	id INTEGER PRIMARY KEY,
	gid INTEGER NOT NULL,
	createdTime INTEGER NOT NULL,
	FOREIGN KEY (gid) REFERENCES games(id)


##大厅
####lobby
	uid INTEGER NOT NULL,
	gid INTEGER NOT NULL,
	status TEXT NOT NULL,
	PRIMARY KEY(uid),
	FOREIGN KEY (uid) REFERENCES users(id),
	FOREIGN KEY (gid) REFERENCES games(id)


##胜场纪录
####winners
	mid INTEGER NOT NULL,
	uid INTEGER NOT NULL,
	PRIMARY KEY(mid, uid),
	FOREIGN KEY (mid) REFERENCES matches(id),
	FOREIGN KEY (uid) REFERENCES users(id)


##负场纪录
####losers
	mid INTEGER NOT NULL,
	uid INTEGER NOT NULL,
	PRIMARY KEY(mid, uid),
	FOREIGN KEY (mid) REFERENCES matches(id),
	FOREIGN KEY (uid) REFERENCES users(id)


##用户权限
####roles
	id INTEGER PRIMARY KEY,
	uid INTEGER NOT NULL,
	access TEXT NOT NULL,
	FOREIGN KEY (uid) REFERENCES users(id)


##参赛视图
####attend(VIEW)
	select users.id uid, matches.id mid
	from users, matches, winners, losers
	where (users.id = winners.uid or users.id = losers.uid) and matches.id = winners.mid and matches.id = losers.mid;


##排名视图
####ranks(VIEW)
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
