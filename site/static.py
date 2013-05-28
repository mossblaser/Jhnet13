#!/usr/bin/python

"""
web.py handlers for various types of static content.
"""

import web

import os
import mimetypes
import datetime


class _StaticBase(object):
	
	def file_path(self, suffix):
		return "%s%s"%(self.path_base, suffix)
	
	
	def format_size(self, size):
		for fmt, div in ( ("%.2fGB", 1024*1024*1024)
		                , ("%.1fMB", 1024*1024)
		                , ("%dKB", 1024)
		                , ("%dB", 1)
		                ):
			if size / div:
				return fmt%(float(size) / div)
	
	
	def GET(self, path):
		# Incase path is None
		if path is None:
			path = ""
		
		if os.path.isdir(self.file_path(path)):
			# Force end with slash for directories
			if not path.endswith("/"):
				raise web.seeother("%s%s/"%(self.url_base, path))
			return self.GET_dir_listing(path)
		else:
			# Force no slash for files
			if path.endswith("/"):
				raise web.seeother("%s%s"%(self.url_base, path[:-1]))
			return self.GET_static_file(path)
	
	
	def GET_dir_listing(self, path):
		# File list generation
		file_list = []
		for file_name in os.listdir(self.file_path(path)):
			file_path = os.path.join(self.file_path(path), file_name)
			(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file_path)
			
			mtime_f = datetime.datetime.fromtimestamp(mtime).strftime("%d-%b-%Y %H:%M")
			size_f  = self.format_size(size)
			
			file_list.append((file_name, mtime_f, size_f, mtime, size))
		
		params = web.input()
		sort_keys = {
			"name" : (lambda (n,m_,s_,m,s) : n),
			"date" : (lambda (n,m_,s_,m,s) : -m), # Reversed
			"size" : (lambda (n,m_,s_,m,s) : s),
		}
		sort_type = params.get("sort",None)
		if sort_type not in sort_keys:
			sort_type = "date"
		sort_key = sort_keys[sort_type]
		
		sort_reverse = "reverse" in params
		
		# Try and find a readme to display
		try:
			readme = open(os.path.join(self.file_path(path), "README.html"), "r").read()
		except IOError:
			readme = ""
		
		# Generate list of breadcrumb links
		cur_path = self.url_base + "/"
		breadcrumb = [ (cur_path, cur_path) ]
		for sub_path in path.split("/")[1:-1]:
			sub_path += "/"
			cur_path += sub_path
			breadcrumb.append((cur_path, sub_path))
		
		return self.listing_template.render(
			title          = "Index of %s%s"%(self.url_base, path),
			readme         = readme,
			breadcrumb     = breadcrumb,
			file_list      = [(n, m, s)
			                  for (n,m,s,m_,s_) in
			                  sorted(file_list, key=sort_key, reverse = sort_reverse)],
			toggle_reverse = "reverse" if not sort_reverse else "",
			name_class     = ["sort-asc","sort-dsc"][sort_reverse]
			                 if sort_type == "name" else "",
			date_class     = ["sort-dsc","sort-asc"][sort_reverse]
			                 if sort_type == "date" else "", # Reversed
			size_class     = ["sort-asc","sort-dsc"][sort_reverse]
			                 if sort_type == "size" else "",
			**self.kwargs
		)
	
	
	def GET_static_file(self, path):
		try:
			file_path = "%s%s"%(self.path_base, path)
			web.header("Content-Type", mimetypes.guess_type(file_path)[0])
			return open(file_path, "rb").read()
		except IOError:
			raise web.notfound()



def StaticBrowseableDir(url_base_, path_base_, listing_template_, **kwargs_):
	"""
	Produces a web.py handler which allows access to static files in the specified
	directory with directory listings.
	"""
	
	class _Static(_StaticBase):
		url_base         = url_base_
		path_base        = path_base_
		listing_template = listing_template_
		kwargs           = kwargs_
	
	return _Static



def StaticDir(url_base_, path_base_):
	"""
	Produces a web.py handler which allows access to static files in the specified
	directory but without directory listings.
	"""
	
	class _Static(_StaticBase):
		url_base  = url_base_
		path_base = path_base_
		def GET_dir_listing(self, path):
			raise web.forbidden()
	
	return _Static


def StaticFile(file_path):
	"""
	Returns a web.py handler which always responds with the specified file.
	"""
	class _StaticFile(_StaticBase):
		def GET(self):
			return self.GET_static_file(file_path)
	
	return _StaticFile


def StaticTemplate(template, **kwargs):
	"""
	Returns a web.py handler which always responds with the specified template
	(taking no arguments).
	"""
	class _StaticTemplate(object):
		def GET(self):
			return template.render(**kwargs)
	
	return _StaticTemplate
