from flask import Flask, Blueprint, Response, request
from sql import client
import json
from utils import utils

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
# @utils.sql_output
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
		return Response(json.dumps(res), 200, content_type="application/json")


BLUEPRINTS = [
	(test_api, '/test'),
	(sql_api, '/sql'),
	(view, '')
]

for blueprint, url_prefix in BLUEPRINTS:
	app.register_blueprint(blueprint, url_prefix=url_prefix)


if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=True)
