#!/usr/bin/python

"""
A web.py handler which removes traling slashes from web addresses.
"""

import web


class Deslash(object):
	
	def GET(self, url):
		raise web.seeother("/%s"%(url.rstrip("/")))


