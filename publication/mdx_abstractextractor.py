#!/usr/bin/env python

"""
Markdown extension which extracts the first paragraph (i.e. the abstract)
"""

from markdown.treeprocessors import Treeprocessor
from markdown.extensions     import Extension

class AbstractExtractorTreeprocessor(Treeprocessor):
	
	def __init__(self, md):
		self.md = md
	
	
	def get_abstract(self, root):
		for child in root:
			if child.tag == "p":
				return child.text
			
			ch_abs = self.get_abstract(child)
			if ch_abs is not None:
				return ch_abs
		
		return None
	
	
	def run(self, root):
		self.md.abstract = self.get_abstract(root)
		return root


class AbstractExtractor(Extension):
	
	def __init__(self, configs):
		pass
	
	def extendMarkdown(self, md, md_globals):
		md.treeprocessors.add('absextractor', AbstractExtractorTreeprocessor(md), '_end')


def makeExtension(configs=None):
	return AbstractExtractor(configs or [])
