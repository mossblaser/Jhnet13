#!./bin/python

import os

import web

from jhnet.app import app

# Ensures that web.py doesn't prefix URLs with "jhnet.py/" whenever it does a
# redirect.
os.environ["REAL_SCRIPT_NAME"] = ""

# A bizarre hack which makes FastCGI work in web.py. Detect that we're running
# under fcgi by checking for the presence of this environment variable
if "SERVER_NAME" in os.environ:
	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)

# Start the fcgi client
if __name__=="__main__":
	app.run()


