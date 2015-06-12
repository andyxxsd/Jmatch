from flask import Flask, Blueprint, Response, request
from Jmatch.sql import client
import json
from Jmatch.utils.utils import utils

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


@sql_api.route("/rebuild", methods=['GET'])
def rebuild():
	client.rebuild()
	return Response("Hello World", 200, content_type="text/html")


@sql_api.route("/<table>", methods=['POST', 'GET'])
@utils.sql_output
def post_object(table):
	if request.method == 'POST':
		print(request.data)
		obj = json.loads(request.data.decode('utf-8'))
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


# @sql_api.before_request
# def check_auth(force_check=False):
#     token = request.cookies.get('token')
#     if not token or force_check:
#         unauth_resp = Response(
#             'Login required',
#             401,
#             {'WWW-Authenticate': 'Basic realm="Please login with OfferCal Account"'}
#             )
#         unauth_resp.set_cookie('token', '', expires=0)
#         auth = request.authorization
#         if not auth:
#             return unauth_resp
#         else:
#             r = requests.post(app.config['API_BASE_URL'] + '/users?action=login',
#                               data=json.dumps({
#                                   'email': auth.username,
#                                   'password': auth.password
#                               }))
#             try:
#                 admin = mongo['roles'].find({'name': 'admin'})[0]
#                 if r.json()['data']['users'][0]['id'] not in admin['userIds']:
#                     return unauth_resp
#                 token = r.json()['data']['users'][0]['accessToken']
#                 resp = redirect('/')
#                 resp.set_cookie('token', token)
#                 return resp
#             except Exception:
#                 return unauth_resp


BLUEPRINTS = [
	(test_api, '/test'),
	(sql_api, '/sql'),
	(view, '')
]

for blueprint, url_prefix in BLUEPRINTS:
	app.register_blueprint(blueprint, url_prefix=url_prefix)
