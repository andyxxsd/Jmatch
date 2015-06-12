#Entrypoint of flask


	Jmatch/__init__.py


#How to start


	./start.sh


or


	gunicorn -w 1 -b 0.0.0.0:4000 Jmatch:app


#How to debug


	python Jmatch/__init__.py


#API


##Insert object into database:

	POST /sql/<table>
	with object json data
		for example:
		{
			"username": "Dear John",
			"password": "break up"
		}

##Get all object from table:

	GET /sql/<table>
	return an array with json data