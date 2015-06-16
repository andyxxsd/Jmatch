#!/usr/bin/env python
import os
import Jmatch
import unittest
import tempfile
import json
import tempfile

headers = {"accesstoken": "thisIsAnAccesstoken"}


def new_user(self, username, password):
	return json.loads(self.app.post("/sql/users", \
		data=json.dumps({"username": username, "password": password}), headers=headers).
		data.decode('utf-8'))[0]


def new_game(self, name, num):
	return json.loads(self.app.post("/sql/games", \
		data=json.dumps({"name": name, "playersNumber": num}), headers=headers).
		data.decode('utf-8'))[0]


def new_match(self, gid, winners, losers):
	return json.loads(self.app.post("/sql/report", \
		data=json.dumps({"gid": gid, "winners": winners, "losers": losers}), headers=headers).
		data.decode('utf-8'))[0]


def pprint(obj):
	print(json.dumps(obj, indent="	"))


class JmatchTestCase(unittest.TestCase):


	def setUp(self):
		self.db_fd, Jmatch.app.config["DB"] = tempfile.mkstemp()
		Jmatch.app.config['TESTING'] = True
		self.app = Jmatch.app.test_client()


	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(Jmatch.app.config['DB'])


	def test_report(self):
		rebuild = self.app.get("/sql/rebuild", headers=headers)
		assert "Success" in rebuild.data.decode('utf-8')

		t1 = new_user(self, "t1", "t1")
		assert "t1" in t1["username"]
		t2 = new_user(self, "t2", "t2")
		assert "t2" in t2["username"]
		game = new_game(self, "Chess", 2)
		assert "Chess" in game["name"]
		match = new_match(self, game["id"], t1["id"], t2["id"])
		assert game["id"] == match["gid"]


	def test_history(self):
		rebuild = self.app.get("/sql/rebuild", headers=headers)
		t1 = new_user(self, "t1", "t1")
		t2 = new_user(self, "t2", "t2")
		game = new_game(self, "Chess", 2)
		match = new_match(self, game["id"], t1["id"], t2["id"])
		history = self.app.get("/sql/history/"+str(t1["id"]), headers=headers)
		assert "win" in history.data.decode('utf-8')


	def test_ready(self):
		rebuild = self.app.get("/sql/rebuild", headers=headers)
		t1 = new_user(self, "t1", "t1")
		t2 = new_user(self, "t2", "t2")
		game = new_game(self, "Chess", 2)
		ready = self.app.get("/sql/ready/" + str(game["id"]), headers={"accesstoken": t1["accesstoken"]})
		assert "OK" in ready.data.decode('utf-8')
		ready = self.app.get("/sql/ready/" + str(game["id"]), headers={"accesstoken": t1["accesstoken"]})
		assert "DEL" in ready.data.decode('utf-8')
		ready = self.app.get("/sql/ready/" + str(game["id"]), headers={"accesstoken": t1["accesstoken"]})
		assert "OK" in ready.data.decode('utf-8')


	def test_ranks(self):
		headers = {"accesstoken": "thisIsAnAccesstoken"}
		rebuild = self.app.get("/sql/rebuild", headers=headers)
		t1 = new_user(self, "t1", "t1")
		t2 = new_user(self, "t2", "t2")
		game = new_game(self, "Chess", 2)
		new_match(self, game["id"], t1["id"], t2["id"])
		new_match(self, game["id"], t1["id"], t2["id"])
		new_match(self, game["id"], t1["id"], t2["id"])
		new_match(self, game["id"], t1["id"], t2["id"])
		ranks = json.loads(self.app.get("/sql/ranks", headers=headers).data.decode('utf-8'))
		assert "t1" in ranks[0]["username"]
		assert ranks[1]["wins"] == 0


	def test_available_opponet(self):
		headers = {"accesstoken": "thisIsAnAccesstoken"}
		rebuild = self.app.get("/sql/rebuild", headers=headers)
		t1 = new_user(self, "t1", "t1")
		t2 = new_user(self, "t2", "t2")
		t3 = new_user(self, "t3", "t3")
		t4 = new_user(self, "t4", "t4")
		chess = new_game(self, "Chess", 2)
		go = new_game(self, "Go", 2)
		new_match(self, chess["id"], t1["id"], t2["id"])
		new_match(self, chess["id"], t1["id"], t3["id"])
		new_match(self, chess["id"], t2["id"], t3["id"])
		new_match(self, go["id"], t1["id"], t3["id"])
		new_match(self, go["id"], t3["id"], t4["id"])
		# ranks = json.loads(self.app.get("/sql/ranks", headers={"accesstoken": t1["accesstoken"]}).data.decode('utf-8'))
		_ = self.app.get("/sql/ready/" + str(chess["id"]), headers={"accesstoken": t1["accesstoken"]})
		_ = self.app.get("/sql/ready/" + str(chess["id"]), headers={"accesstoken": t2["accesstoken"]})
		_ = self.app.get("/sql/ready/" + str(chess["id"]), headers={"accesstoken": t3["accesstoken"]})
		_ = self.app.get("/sql/ready/" + str(chess["id"]), headers={"accesstoken": t4["accesstoken"]})
		ao = json.loads(self.app.get("/sql/ao", headers={"accesstoken": t1["accesstoken"]}).data.decode('utf-8'))
		assert ao[0]["wins"] == 2
		assert ao[1]["wins"] == 1
		assert ao[2]["wins"] == 0
		match = json.loads(self.app.get("/sql/match", headers={"accesstoken": t1["accesstoken"]}).data.decode('utf-8'))
		assert match[0]["username"] == "t2"
		match = json.loads(self.app.get("/sql/match", headers={"accesstoken": t3["accesstoken"]}).data.decode('utf-8'))
		assert match[0]["username"] == "t2"


if __name__ == '__main__':
	unittest.main()