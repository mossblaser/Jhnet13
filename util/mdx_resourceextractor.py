#!/usr/bin/env python

"""
Markdown extension which maps all local filenames (i.e. file://) to a
subdirectory specified by the config variable "resource_dir". Relative paths are
presumed to be relative to "relative_path" or the current working directory if
not given.

Returns a list of (local_path, desired_path) in md.resources where local_path is
the path to the file on the local machine and desired_path is the new path.
"""

from markdown.treeprocessors import Treeprocessor
from markdown.extensions     import Extension

import os

from util import unique

class ResourceExtractorTreeprocessor(Treeprocessor):
	
	# A list of types of tags which point to resources and the attribute which
	# contains the address of the resource.
	RESOURCE_TAGS = {
		"img": "src",
		"a":   "href",
	}
	
	def __init__(self, md, configs):
		self.md = md
		self.configs = configs
	
	
	def remap_resources(self, root, local_file_paths = None, desired_file_names = None):
		local_file_paths   = local_file_paths   if local_file_paths   is not None else []
		desired_file_names = desired_file_names if desired_file_names is not None else []
		
		for child in root:
			if child.tag in ResourceExtractorTreeprocessor.RESOURCE_TAGS:
				attrib = ResourceExtractorTreeprocessor.RESOURCE_TAGS[child.tag]
				file_path = child.attrib[attrib]
				if file_path.startswith("file://"):
					local_file_path = os.path.join( self.configs.get("relative_path",".")
					                              , file_path[len("file://"):]
					                              )
					desired_file_name = unique(os.path.basename(local_file_path), desired_file_names)
					
					child.attrib[attrib] = "%s/%s"%(self.configs["resource_dir"],desired_file_name)
					
					local_file_paths.append(local_file_path)
					desired_file_names.append(desired_file_name)
			
			# Recurse
			self.remap_resources(child, local_file_paths, desired_file_names)
		
		
		# Return with the resource dirs prefixed
		return zip(local_file_paths,
		           ( "%s/%s"%(self.configs["resource_dir"], dfn)
		             for dfn in desired_file_names)
		           )
		
	
	
	def run(self, root):
		self.md.resources = self.remap_resources(root)
		return root


class ResourceExtractor(Extension):
	
	def __init__(self, configs):
		self.configs = dict(configs)
	
	def extendMarkdown(self, md, md_globals):
		md.treeprocessors.add(
			'resourceextractor',
			ResourceExtractorTreeprocessor(md, configs = self.configs),
			'_end'
		)


def makeExtension(**kwargs):
	return ResourceExtractor(kwargs.get("configs", {}))

