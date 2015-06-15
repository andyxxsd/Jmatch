# -*- coding: utf-8 -*-

import json
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
				data = json.dumps(items, indent="	")
				# if keywords.get('obj_id', None) is not None or keywords.get('data', None) is not None:
				#	 if len(items) > 0:
				#		 data = json_util.dumps(items[0])
				#	 else:
				#		 abort(404)
				# else:
				#	 data = json_util.dumps(items)
				print(data)
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
