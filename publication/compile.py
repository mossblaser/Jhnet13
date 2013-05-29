#!/usr/bin/env python

"""
Compiler for publications described in markdown format.

Usage:

	compile.py input_file.md [output_path]
	
	Where input-file is a markdown file and output_path is optionally a path to
	place the output. If left out, output is placed in the current directory. If
	ends with "/" then the input_file's basename (without extension) is used as
	the article name. Otherwise, the basename of this path is used as the output
	name and the basepath the location to place the files.
	
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

import os

from util import unique

def process_markdown(input_markdown, output_name):
	"""
	Produces the html file, toc file, meta file and a list of (local_file,
	target_name) pairs where local_file is a file on the local system and
	target_name is the name of the file when placed in [output_name]/*
	"""
	md = markdown.Markdown( extensions=[ 'meta'
	                                   , 'codehilite'
	                                   , 'footnotes'
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
	title = md.Meta.get("title", [title])[0]
	
	# Choose document subtitle (only available from metadata)
	subtitle = md.Meta.get("subtitle", [None])[0]
	
	# Get the image from the metadata
	img = md.Meta.get("img", [None])[0]
	img_alt = md.Meta.get("img_alt", [None])[0]
	
	# The abstract should be taken to be the first paragraph.
	abstract = md.abstract if md.abstract is not None else ""
	
	# Get the list of tags
	tags = md.Meta.get("tags", [])
	
	# Get the show option
	show = md.Meta.get("show", ["True"])[0] == "True"
	
	files = md.resources
	
	# Add the article image to the list of files
	if img is not None and img.startswith("file://"):
		img = img[len("file://"):]
		img_output_name = "%s/%s"%(output_name,
		                           unique(os.path.basename(img),
		                                  [f.split("/")[-1] for (_,f) in files]))
		files.append((img, img_output_name))
		img = img_output_name
	
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
	
	# The input file implies an output name which may be used
	input_suggested_output_name, _ = os.path.splitext(input_markdown_file_name)
	
	# Output goes to what name...
	if len(sys.argv) > 2:
		output_path = sys.argv[2]
		if output_path.endswith("/"):
			output_name = input_suggested_output_name
		else:
			output_name = os.path.basename(output_path)
			output_path = os.path.dirname(output_path)
	else:
		output_path = "."
		output_name = input_suggested_output_name
	
	output_file_name = os.path.join(output_path, output_name)
	
	html, toc, meta, files = process_markdown(input_markdown_file.read(), output_name)
	
	# Make output file directory
	try:
		os.mkdir(output_path)
	except OSError:
		# Directory exists
		pass
	
	with open("%s.html"%output_file_name, "w") as f:
		f.write(html)
	
	with open("%s.toc"%output_file_name, "w") as f:
		json.dump(toc, f)
	
	with open("%s.meta"%output_file_name, "w") as f:
		json.dump(meta, f)
	
	# Make output file directory
	try:
		os.mkdir(output_file_name)
	except OSError:
		# Directory exists
		pass
	
	# Copy files into output file directory
	for local_path, target_path in files:
		target_path = os.path.join(output_path, target_path)
		try:
			shutil.copy(local_path, target_path)
		except IOError, e:
			sys.stderr.write("WARNING: Could not copy %s to %s: %s\n"%(
				local_path, target_path, repr(e)
			))
