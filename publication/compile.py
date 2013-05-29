#!/usr/bin/env python

"""
Compiler for publications described in markdown format.

Usage:

	compile.py input_file.md [output_name]
	
	Where input-file is a markdown file and output_name is optionally a name to call
	the output.
	
Produces:
	[output_name].html -- a HTML file containing the body HTML of the publication.
	[output_name].toc -- a JSON file containing a list of pairs (level, toc_entry, anchor)
	[output_name].meta -- a JSON file containing a dictionary:
	[output_name]/* -- a directory containing all assets used by the publication
		{
			"url" : "output_name",
			"title" : ,
			"subtitle" : ,
			"img" : ,
			"img_alt" : ,
			"abstract" : ,
			"tags" : ,
			"show" : ,
		}
"""

import markdown


def process_markdown(input_markdown, output_name):
	"""
	Produces the html file, toc file, meta file and a list of (local_file,
	target_name) pairs where local_file is a file on the local system and
	target_name is the name of the file when placed in [output_name]/*
	"""
	md = markdown.Markdown( extensions=[ 'meta'
	                                   , 'resourceextractor'
	                                   , 'abstractextractor'
	                                   , 'tocextractor'
	                                   ]
	                      , extension_configs = {
	                          "resourceextractor":
	                            (("resource_dir",output_name),),
	                        }
	                      )
	
	# Basic HTML conversion
	html = md.convert(input_markdown)
	
	# Generate table of contents
	toc  = md.toc
	
	# Choose document title (default to the output name)
	title = output_name
	# Use the first heading if possible
	if len(toc) > 0:
		title = toc[0][1]
	# Better yet, get the explicitly given metadata
	title = md.Meta.get("title", title)
	
	# Choose document subtitle (only available from metadata)
	subtitle = md.Meta.get("subtitle", None)
	
	# Get the image from the metadata
	img = md.Meta.get("img", None)
	img_alt = md.Meta.get("img_alt", None)
	
	# The abstract should be taken to be the first paragraph.
	abstract = md.abstract if md.abstract is not None else ""
	
	# Get the list of tags
	tags = md.Meta.get("tags", [])
	# Ensure it is a list...
	if isinstance(tags, basestring):
		tags = [tags]
	
	# Get the show option
	show = md.Meta.get("show", "False") == "True"
	
	
	# Generate meta-data
	meta_data = {
		"url" : output_name,
		"title" : title,
		"subtitle" : subtitle,
		"img" : img,
		"img_alt" : img_alt,
		"abstract" : abstract,
		"tags" : tags,
		"show" : show,
	}
	
	files = md.resources
	
	return html, toc, meta_data, files
	



if __name__=="__main__":
	import sys, os, shutil
	import json
	
	# Input comes from stdin
	if len(sys.argv) > 1 or sys.argv[1] == "-":
		input_markdown_file_name = sys.argv[1]
		input_markdown_file = open(input_markdown_file_name)
	else:
		input_markdown_file_name = "stdin"
		input_markdown_file = sys.stdin
	
	# Output goes to what name...
	if len(sys.argv) > 2:
		output_name = sys.argv[2]
	else:
		output_name, extension = os.path.splitext(input_markdown_file_name)
	
	html, toc, meta, files = process_markdown(input_markdown_file.read(), output_name)
	
	
	with open("%s.html"%output_name, "w") as f:
		f.write(html)
	
	with open("%s.toc"%output_name, "w") as f:
		json.dump(toc, f)
	
	with open("%s.meta"%output_name, "w") as f:
		json.dump(meta, f)
	
	# Make output file directory
	try:
		os.mkdir(output_name)
	except OSError:
		# Directory exists
		pass
	
	# Copy files into output file directory
	for local_path, target_path in files:
		try:
			shutil.copy(local_path, target_path)
		except IOError, e:
			sys.stderr.write("WARNING: Could not copy %s to %s: %s\n"%(
				local_path, target_path, repr(e)
			))
