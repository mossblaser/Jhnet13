#!/usr/bin/env python

"""
Markdown extension which does toc extraction.
"""

from markdown.treeprocessors import Treeprocessor
from markdown.extensions     import Extension

from markdown.extensions.headerid import slugify

from util import unique

class ToCExtractorTreeprocessor(Treeprocessor):
	
	HEADINGS = ["h%d"%level for level in range(1,7)]
	
	
	def __init__(self, md):
		self.md = md
	
	
	def get_headings(self, root):
		headings = []
		
		for child in root:
			if child.tag in ToCExtractorTreeprocessor.HEADINGS:
				headings.append(child)
			
			headings.extend(self.get_headings(child))
		
		return headings
	
	
	def allocate_anchors(self, headings):
		ids = []
		labels = []
		levels = []
		
		for heading in headings:
			# Pick an ID
			id = unique(slugify(heading.text, "-"), ids)
			
			# Assign the ID to the heading
			heading.attrib["id"] = id
			
			# Record it
			ids.append(id)
			labels.append(heading.text)
			levels.append(int(heading.tag[1]))
		
		return zip(levels, labels, ids)
	
	
	def run(self, root):
		headings = self.get_headings(root)
		self.md.toc = self.allocate_anchors(headings)
		return root


class ToCExtractor(Extension):
	
	def __init__(self, configs):
		pass
	
	def extendMarkdown(self, md, md_globals):
		md.treeprocessors.add('tocextractor', ToCExtractorTreeprocessor(md), '_end')


def makeExtension(configs=None):
	return ToCExtractor(configs or [])
