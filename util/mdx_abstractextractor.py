#!/usr/bin/env python

"""
Markdown extension which extracts the first paragraph (i.e. the abstract)
"""

from markdown.treeprocessors import Treeprocessor
from markdown.extensions     import Extension
from markdown.util           import HTML_PLACEHOLDER_RE

class AbstractExtractorTreeprocessor(Treeprocessor):
	
	def __init__(self, md):
		self.md = md
	
	
	def get_text(self, root):
		return (root.text or "")\
		       + "".join(self.get_text(c) for c in root) \
		       + (root.tail or "")
	
	
	def get_abstract(self, root):
		for child in root:
			if child.tag == "p":
				text = self.get_text(child)
				if text.strip() != "" and HTML_PLACEHOLDER_RE.match(text) is None:
					return text
			
			ch_abs = self.get_abstract(child)
			if ch_abs is not None:
				return ch_abs
		
		return None
	
	
	def run(self, root):
		self.md.abstract = self.get_abstract(root)
		return root


class AbstractExtractor(Extension):
	
	def __init__(self, **kwargs):
		pass
	
	def extendMarkdown(self, md, md_globals={}):
		md.treeprocessors.register(AbstractExtractorTreeprocessor(md), 'absextractor', -100)


def makeExtension(**kwargs):
	return AbstractExtractor(**kwargs)
