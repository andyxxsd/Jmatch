# 我的锅游戏匹配平台(Jmatch) API Documentation
#### use "accesstoken: [accessToken]" in the header
#### alway sending/returning endpoint's corresponding object unless mentioned


## Unauthorized API

#### Login:
	POST /login
	Parameters:
		username: the username of your account, e.g. 'Skylar.Zheng'
		password: the password of your account, e.g. '123456'

## Authorized API - Manipulating database

#### Fetch data:
	GET /sql/<table>
	You will get data from <table> in JSON format.
	e.g. '[{"username": "Skylar.Zheng", "accesstoken": "thisIsAnAccesstoken"}]'

#### Add entry:
	POST /sql/<table>
	with <table> object in JSON format
	server will automatically generate id
	Example:
		POST /sql/games
		'{"name": "LOL", "playersNumber": 10}'

#### Rebuild database:
	GET /sql/rebuild
	This is an DANGEROUS api. Old data will be lost.
	Mostly it's used for debugging :)


## Authorized API - Special Occation (Like reporting matches, fetching history etc.)
	
#### Report the result of a match:
	POST /sql/report
	with JSON object:
		gid: the id of the game
		winners: the uid of winners, could be array or string
		winners: the uid of losers, could be array or string
	Example:
		POST /sql/report
		'{"gid": 1, "winners": 1025, "losers": 1026}'

		POST /sql/report
		'{"gid": 1, "winners": [1025, 1026, 1027], "losers": [1028, 1029, 1030]}'

#### Get ready:
    GET /sql/ready/<gid>
    Get ready to match for the game which id is <gid>
	    It has a logic that toggle you from the matching pool.
	    First time you request this API, you are added to the matching pool. Returns "OK".
	    Before you get matched, you request this API again, you will be removed from matching pool. Returns "DEL".

#### Get available opponet list:
	GET /sql/ao
	Return a list of object:
		uid: the user id of your available opponet
		wins: the win matches of your available opponet
	Example:
		GET /sql/ao
		'[{"uid": 1024, "wins":9}, {"uid": 1025, "wins":0}]'

#### Get history of you:
	GET /sql/history
	Return a list of object:
		mid: the match id
		game: the game you played
		createdTime: when you played this match
		result: "win" or "lose"
	Example:
		GET /sql/history
		'[{"game": "Chess","createdTime": "06-27 00:12","result": "lose","mid": 10},
		  {"game": "Chess","createdTime": "06-27 00:12","result": "lose","mid": 9}]'
