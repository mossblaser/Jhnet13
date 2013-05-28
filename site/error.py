#!/usr/bin/python

"""
A web.py handler which displays something friendly on a 404.
"""

import web

def NotFound(template, **kwargs):
	def notfound():
		raise web.notfound(template.render(
			title = "Page Not Found",
			url   = web.ctx.path,
			**kwargs
		))
	return notfound


def InternalError(template, **kwargs):
	def internalerror():
		raise web.internalerror(template.render(
			title = "Internal Error",
			url   = web.ctx.path,
			**kwargs
		))
	return internalerror
