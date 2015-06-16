#!/usr/bin/env python
import os
import Jmatch
import unittest
import tempfile
import json

class JmatchTestCase(unittest.TestCase):

	def setUp(self):
		Jmatch.app.config['TESTING'] = True
		self.app = Jmatch.app.test_client()
		
	def tearDown(self): pass

	def test_report(self):
		headers = {"accesstoken": "thisIsAnAccesstoken"}
		rebuild = self.app.get("/sql/rebuild", headers=headers)
		assert "Success" in rebuild.data.decode('utf-8')

		t1 = self.app.post("/sql/users", data=json.dumps({"username": "t1", "password": "t1"}), headers=headers)
		assert "t1" in t1.data.decode('utf-8')
		t1 = json.loads(t1.data.decode('utf-8'))[0]

		t2 = self.app.post("/sql/users", data=json.dumps({"username": "t2", "password": "t2"}), headers=headers)
		assert "t2" in t2.data.decode('utf-8')
		t2 = json.loads(t2.data.decode('utf-8'))[0]

		game = self.app.post("/sql/games", data=json.dumps({"name": "Chess", "playersNumber": 2}), headers=headers)
		assert "Chess" in game.data.decode('utf-8')
		game = json.loads(game.data.decode('utf-8'))[0]

		match = self.app.post("/sql/report", data=json.dumps({"gid": game["id"], "winners": t1["id"], "losers": t2["id"]}), headers=headers)
		assert str(game["id"]) in match.data.decode('utf-8')
		match = json.loads(match.data.decode('utf-8'))[0]

	def test_history(self):
		headers = {"accesstoken": "thisIsAnAccesstoken"}
		rebuild = self.app.get("/sql/rebuild", headers=headers)
		t1 = self.app.post("/sql/users", data=json.dumps({"username": "t1", "password": "t1"}), headers=headers)
		t1 = json.loads(t1.data.decode('utf-8'))[0]
		t2 = self.app.post("/sql/users", data=json.dumps({"username": "t2", "password": "t2"}), headers=headers)
		t2 = json.loads(t2.data.decode('utf-8'))[0]
		game = self.app.post("/sql/games", data=json.dumps({"name": "Chess", "playersNumber": 2}), headers=headers)
		game = json.loads(game.data.decode('utf-8'))[0]
		match = self.app.post("/sql/report", data=json.dumps({"gid": game["id"], "winners": t1["id"], "losers": t2["id"]}), headers=headers)
		history = self.app.get("/sql/history/"+str(t1["id"]), headers=headers)
		assert "win" in history.data.decode('utf-8')

if __name__ == '__main__':
	unittest.main()