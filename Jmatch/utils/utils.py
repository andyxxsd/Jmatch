# -*- coding: utf-8 -*-

import json
import time
from flask import Response, request, abort

class utils(object):
	@staticmethod
	def sql_output(f):
		def decorator(**keywords):
			result = f(**keywords)
			if isinstance(result, str) :
				status_code = 200
				if result != 'OK':
					status_code = 400
				return Response(result, status_code)
			else:
				items = [item for item in result]
				# Convert timestamp to datetime
				for v in items:
					for k in v.keys():
						if k == "createdTime":
							v[k] = time.ctime(v[k])
				data = json.dumps(items, indent="	")
				resp = Response(
					response=data,
					status=200,
					mimetype="application/json"
				)
				return resp
		decorator.__name__ = f.__name__
		return decorator

	# @staticmethod
	# def mongo_input(f):
	#	 def decorator(**keywords):
	#		 keywords['data'] = json_util.loads(request.data)
	#		 return f(**keywords)
	#	 decorator.__name__ = f.__name__
	#	 return decorator

def rows_to_dicts(rows):
	res = []
	for row in rows:
		cur = {}
		for key in row.keys():
			cur[key] = row[key]
		res.append(cur)
	return res