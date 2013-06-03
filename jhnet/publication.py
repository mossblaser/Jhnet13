#!/usr/bin/python

"""
A web.py handler for publication/blog-style content.
"""

import web

import os
import re
import json
import mimetypes

tags_re = re.compile("^/tag/([^/]*)$")
pub_re  = re.compile("^/([^/]*)$")
stat_re = re.compile("^/([^/]*)/(.*)$")

def Publications(url_base_, pub_base_, title_,
                 listing_template_, pub_template_, **kwargs_):
	"""
	A publication serving handler.
	
	url_base_ is the base of the urls used to access this publications handler
	(not including trailing slash).
	
	pub_base_ is the file-system path to the publication directory. In this
	directory the following directory structure is expected:
		
		/README.html is a HTML snippet which describes the publications as a whole.
		(optional)
		
		/toc.json is a JSON file containing a list of dictionaries like so, one for
		each publication:
			
			{
				"url"      : publication url,
				"title"    : publication title,
				"subtitle" : publication subtitle,
				"img"      : publication image (or null if no image to show),
				"img_alt"  : publication image alt-text (if img defined),
				"abstract" : html snippet describing the article,
				"tags"     : a list of tags describing the article,
				"show"     : bool should the publication be listed?,
			}
		
		/[pub_url].html for each publication which contains the content HTML for the
		publication.
		
		/[pub_url].toc for each publication which contains a JSON list of pairs
		(toc_entry, html_anchor). (optional)
		
		/[pub_url]/* for each publication, any static files (e.g. images)
	
	title_ is the suffix to be addded to the page titles.
	
	listing_template_ is a mako template for the listings page. Specifies:
		
		title to be the page title
		
		heading to be the page heading
		
		readme to be a HTML field to describe the publications as a whole
		
		tags to be a list of (tag, url, active) pairs for tag listings pages
		
		publications to be a list of (pub_title, pub_subtitle, pub_url, img_url,
		img_alt, pub_abstract, pub_tags) tuples for each publication. Here pub_tags
		is a list of (tag_name, tag_url) pairs.
	
	pub_template_ is a mako template for a publication. Specifies:
		
		title to be the page title
		
		content to be HTML page contents
		
		toc to be a list of (entry, url, ) for the table of contents
	"""
	
	class _Publications(object):
		
		url_base         = url_base_
		pub_base         = pub_base_
		title            = title_
		listing_template = listing_template_
		pub_template     = pub_template_
		kwargs           = kwargs_
		
		
		def load_json(self, file_name):
			"""
			Load the ToC JSON file and return the data within
			"""
			with open(file_name, "r") as toc_file:
				return json.load(toc_file)
		
		
		def get_tags(self, toc):
			tags = set()
			for pub in toc:
				if pub["show"]:
					tags = tags.union(pub["tags"])
			return sorted(tags)
		
		
		def to_url(self, text):
			return text.lower().replace(" ", "+")
		
		
		def GET(self, url):
			# Nothing should end with a slash
			if url.endswith("/"):
				raise web.seeother(self.url_base + url.rstrip("/"))
			
			# Get the main listing
			if url == "":
				return self.GET_listing()
			
			# Get the listing for the given tag
			tag_match = tags_re.match(url)
			if tag_match:
				return self.GET_listing(tag_match.group(1))
			
			# It must be a publication
			pub_match = pub_re.match(url)
			if pub_match:
				return self.GET_publication(pub_match.group(1))
			
			# Otherwise it'll be a static file
			stat_match = stat_re.match(url)
			if stat_match:
				return self.GET_static_file(stat_match.group(1), stat_match.group(2))
			
			# Or just unknown...
			raise web.notfound()
		
		
		def GET_listing(self, tag_url = None):
			toc = self.load_json(os.path.join(self.pub_base, "toc.json"))
			tags = self.get_tags(toc)
			tag_urls = map(self.to_url, tags)
			
			# Check that the tag exists
			if tag_url is not None and tag_url not in tag_urls:
				raise web.notfound()
			
			# Current tag name
			tag = tags[tag_urls.index(tag_url)] if tag_url is not None else None
			
			# Set the page title
			if tag_url is None:
				title = self.title
			else:
				title = "%s - %s"%(tag, self.title)
			
			# Get the README, if present
			try:
				readme = open(os.path.join(self.pub_base, "README.html"), "r").read()
			except IOError:
				readme = ""
			
			# Get the link to a given tag
			def tag_link(tag_name):
				return "%s/tag/%s"%(self.url_base, self.to_url(tag_name))
			
			# Generate the list of tags
			tag_menu = [("Any", self.url_base, tag_url is None)]
			for tag_, url_ in zip(tags, tag_urls):
				tag_menu.append((tag_, tag_link(tag_),url_ == tag_url))
			
			# Generate list of publications
			publications = []
			for pub in toc:
				if pub["show"] and (tag is None or tag in pub["tags"]):
					publications.append((
						pub["title"],
						pub["subtitle"],
						"%s/%s"%(self.url_base, pub["url"]),
						"%s/%s"%(self.url_base, pub["img"]) if pub["img"] is not None else None,
						pub["img_alt"],
						pub["abstract"],
						[(t, tag_link(t)) for t in sorted(pub["tags"])],
					))
				else:
					print "hidden", pub["show"], tag is None, tag in pub["tags"]
			
			# Render the page
			web.header('Content-Type', 'text/html')
			return self.listing_template.render(
				title        = title,
				heading      = self.title,
				readme       = readme,
				tags         = tag_menu,
				publications = publications,
				**self.kwargs
			)
		
		
		def GET_publication(self, publication_url):
			# Get info from the publications toc
			toc = self.load_json(os.path.join(self.pub_base, "toc.json"))
			
			# Check publication exists
			for pub in toc:
				if publication_url == pub["url"]:
					break
				pub = None
			if pub is None:
				raise web.notfound()
			
			# Load the publication's body
			pub_html = open(os.path.join(self.pub_base, "%s.html"%publication_url), "r").read()
			
			# Try to load the publication's ToC
			try:
				pub_toc = self.load_json(os.path.join(self.pub_base, "%s.toc"%publication_url))
			except IOError:
				pub_toc = None
			
			# Render the page
			web.header('Content-Type', 'text/html')
			return self.pub_template.render(
				title   = "%s - %s"%(pub["title"], self.title),
				content = pub_html,
				toc     = pub_toc,
				**self.kwargs
			)
		
		
		def GET_static_file(self, publication_name, path):
			file_path = os.path.join(self.pub_base, publication_name, path)
			try:
				web.header("Content-Type", mimetypes.guess_type(file_path)[0])
				with open(file_path, "rb") as f:
					data = True
					while data:
						data = f.read(100)
						yield data
			except IOError:
				raise web.notfound()
	
	return _Publications
