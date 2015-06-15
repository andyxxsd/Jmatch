from flask import Flask, Blueprint, Response, request, abort
from Jmatch.sql import client
import json
import hashlib
from Jmatch.utils.utils import utils
import traceback

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
	print(cur.fetchone())
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
	if client.verifyUser(accesstoken=accesstoken) == None:
		abort(401)


@sql_api.route("/rebuild", methods=['GET'])
def rebuild():
	client.rebuild()
	return "Successfully rebuild"


@sql_api.route("/<table>", methods=['POST', 'GET'])
@utils.sql_output
def post_object(table):
	try:
		if request.method == 'POST':
			print(request.data)
			obj = json.loads(request.data.decode('utf-8'))
			if table == 'users' and 'accesstoken' not in obj:
				obj['accesstoken'] = hashlib.sha1(obj['username'].encode('utf-8')).hexdigest()
			client.insert(table, list(obj.keys()), list(obj.values()))
			return "OK"
		if request.method == 'GET':
			results = client.selectAll(table)
			res = []
			for result in results:
				cur = {}
				for key in result.keys():
					cur[key] = result[key]
				res.append(cur)
			return res
	except Exception as e:
		print(e)
		return e.__str__()


BLUEPRINTS = [
	(test_api, '/test'),
	(sql_api, '/sql'),
	(view, '')
]

for blueprint, url_prefix in BLUEPRINTS:
	app.register_blueprint(blueprint, url_prefix=url_prefix)
