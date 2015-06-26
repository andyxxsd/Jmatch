from flask import Flask, Blueprint, Response, request, abort
from Jmatch.sql import client
import json
import time
import hashlib
from Jmatch.utils.utils import *
import traceback
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile("config.py")

test_api = Blueprint('test', __name__)
sql_api = Blueprint('sql', __name__)
view = Blueprint('view', __name__)


@test_api.route("/hello",  methods=['GET'])
def hello():
	return "Hello World!"


@test_api.route("/",  methods=['GET'])
def helloSql():
	conn, cur = client.connect()
	cur.execute("select 1+1 as sum")
	cur.close()
	return Response("Pig", 200, content_type="text/html")


@app.route("/login", methods=['POST'])
@utils.sql_output
def login():
	auth = json.loads(request.data.decode('utf-8'))
	accesstoken = client.verifyUser(auth['username'], auth['password'])
	if accesstoken is None:
		abort(401)
	client.delete("lobby", ["uid"], [client.verifyUser(accesstoken=accesstoken)])
	return rows_to_dicts(client.select("users", ["accesstoken"], [accesstoken]));


@sql_api.before_request
def check_auth():
	accesstoken = request.headers.get('accesstoken')
	if accesstoken != 'thisIsAnAccesstoken' or request.path != '/sql/rebuild':
		if not accesstoken:
			unauth_resp = Response(
				'Login required',
				401,
				{'WWW-Authenticate': 'Basic realm="Login Required"'}
				)
			auth = request.authorization
			if not auth:
				return unauth_resp
			else:
				accesstoken = client.verifyUser(auth.username, auth.password)
				if accesstoken == None:
					return unauth_resp
		request.uid = client.verifyUser(accesstoken=accesstoken)
		if request.uid == None:
			abort(401)


@sql_api.route("/rebuild", methods=['GET'])
def rebuild():
	client.rebuild()
	return "Successfully rebuild"


@sql_api.route("/<table>", methods=['POST', 'GET'])
@utils.sql_output
def post_get_object(table):
	try:
		if request.method == 'POST':
			obj = json.loads(request.data.decode('utf-8'))
			if table == 'users' and 'accesstoken' not in obj:
				obj['accesstoken'] = hashlib.sha1(obj['username'].encode('utf-8')).hexdigest()
			return rows_to_dicts([client.insert(table, list(obj.keys()), list(obj.values()))])
		if request.method == 'GET':
			return rows_to_dicts(client.selectAll(table))
	except Exception as e:
		print(e)
		return e.__str__()


# obj:
# 	gid = game id
# 	winners = [uid, uid, uid...] or uid
# 	losers = [uid, uid, uid...] or uid
@sql_api.route("/report", methods=['POST'])
@utils.sql_output
def report():
	obj = json.loads(request.data.decode('utf-8'))
	if not isinstance(obj['winners'], list):
		obj['winners'] = [obj['winners']]
	if not isinstance(obj['losers'], list):
		obj['losers'] = [obj['losers']]
	match = client.insert('matches', ["gid", "createdTime"], [obj["gid"], int(time.time())])
	for v in obj['winners']:
		_ = client.insert('winners', ["mid", "uid"], [match["id"], v])
	for v in obj['losers']:
		_ = client.insert('losers', ["mid", "uid"], [match["id"], v])
	return rows_to_dicts([match])


@sql_api.route("/ready/<gid>", methods=['GET'])
def ready(gid):
	if client.check("lobby", ["uid"], [request.uid]):
		client.delete("lobby", ["uid"], [request.uid])
		return "DEL"
	else:
		client.insert("lobby", ["uid", "gid", "status"], [request.uid, gid, "ready"])
		return "OK"


@sql_api.route("/match", methods=['GET'])
@utils.sql_output
def match(): 
	ao = client.available_opponet(request.uid)
	me = client.select("ranks", ["id"], [request.uid])[0]
	best_match = None
	for opponet in ao:
		if opponet["uid"] != me["id"] and (best_match is None or abs(opponet["wins"]-me["wins"])<best_match["abs"]):
			best_match={
				"abs": abs(opponet["wins"]-me["wins"]),
				"uid": opponet["uid"],
			}
	if best_match is None:
		return "Match failed"
	return rows_to_dicts(client.select("users", ["id"], [best_match["uid"]]))


@sql_api.route("/ao", methods=['GET'])
@utils.sql_output
def available_opponet():
	return rows_to_dicts(client.available_opponet(request.uid))


@sql_api.route("/history", methods=['GET'])
@utils.sql_output
def history():
	return rows_to_dicts(client.history(request.uid))


@sql_api.route("/history/<uid>", methods=['GET'])
@utils.sql_output
def history_uid(uid):
	return rows_to_dicts(client.history(uid))


BLUEPRINTS = [
	(test_api, '/test'),
	(sql_api, '/sql'),
	(view, '')
]

for blueprint, url_prefix in BLUEPRINTS:
	app.register_blueprint(blueprint, url_prefix=url_prefix)
