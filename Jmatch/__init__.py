from flask import Flask, Blueprint, Response, request, abort
from Jmatch.sql import client
import json
import time
import hashlib
from Jmatch.utils.utils import *
import traceback
from datetime import datetime

app = Flask(__name__)

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
def login():
	auth = json.loads(request.data.decode('utf-8'))
	accesstoken = client.verifyUser(auth['username'], auth['password'])
	if accesstoken is None:
		abort(401)
	return accesstoken


@sql_api.before_request
def check_auth():
	accesstoken = request.headers.get('accesstoken')
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
