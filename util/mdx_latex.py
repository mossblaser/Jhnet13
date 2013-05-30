#!/usr/bin/env python

r"""
Markdown extension which allows inline LaTeX.

Adds the syntax::
	
	\begin{latex}[Alt-text]
		Some \LaTeX{} here!
	\end{latex}

Which produces an image with the given latex rendered in it and the alt-text
specified. The \begin and \end lines must be at indent level zero. Note:
alt-text should be unique within a document as filenames for PNGs are derrived
from the alt-text.

The PNG file will be placed in the directory configs["latex_img_dir"].
"""

from markdown.blockprocessors import BlockProcessor
from markdown.extensions      import Extension

from markdown.extensions.headerid import slugify

from mako.template import Template

from subprocess import Popen

import re
import os, sys, tempfile, shutil



class LaTeXBlockProcessor(BlockProcessor):
	
	ENV_START = r"\begin{latex}["
	ENV_END   = "\n" + r"\end{latex}"
	
	latex_re = re.compile(r"\\begin\{latex\}\[([^]]*)\]"
	                      + r"(.*)"
	                      + r"^\\end\{latex\}\s*"
	                     , re.MULTILINE | re.DOTALL)
	
	# How many times to build with latex
	LATEX_BUILDS = 2
	
	# A template for a latex file that renders to one file
	LATEX_TEMPLATE = Template(r"""
		%% Only build the bare minimum
		%%\documentclass{minimal}
		\documentclass[border=0pt]{standalone}
		
		\usepackage{amsmath}
		\usepackage{amssymb}
		
		\usepackage{graphicx}
		
		\usepackage{tikz}
		\usetikzlibrary{positioning}
		
		\begin{document}
				${document}
		\end{document}
	""")
	
	
	def __init__(self, configs, *args, **kwargs):
		self.configs = dict(configs)
		BlockProcessor.__init__(self, *args, **kwargs)
	
	
	def render_latex(self, latex_snippet, output_png_file):
		"""
		Takes a snippet of latex and produces a png at the filename specified.
		"""
		tmp_dir = tempfile.mkdtemp(prefix = "mdx_latex_")
		tex_file = os.path.join(tmp_dir, "file.tex")
		pdf_file = os.path.join(tmp_dir, "file.pdf")
		
		try:
			# Generate the tex file
			tex = LaTeXBlockProcessor.LATEX_TEMPLATE.render(document = latex_snippet)
			with open(tex_file, "w") as f:
				f.write(tex)
			
			# Try and build the file
			for build_num in range(LaTeXBlockProcessor.LATEX_BUILDS):
				p = Popen( ["pdflatex", "-shell-escape", "-halt-on-error", tex_file]
				         , cwd = tmp_dir
				         , stdin  = None
				         , stdout = sys.stderr
				         , stderr = sys.stderr
				         )
				if p.wait() != 0:
					raise Exception("LaTeX Compilation Failed for:\n%s"%latex_snippet)
			
			# Convert to PNG
			p = Popen( ["convert", "-density", "110x110", pdf_file, output_png_file]
			         , stdin  = None
			         , stdout = sys.stderr
			         , stderr = sys.stderr
			         )
			if p.wait() != 0:
				raise Exception("Converting PDF to PNG failed for:\n%s"%latex_snippet)
			
		finally:
			shutil.rmtree(tmp_dir)

	
	
	def test(self, parent, block):
		# Are we either in a latex environment or does this block begin one?
		return block.startswith(LaTeXBlockProcessor.ENV_START)
	
	
	def run(self, parent, blocks):
		accumulated_tex_blocks = []
		
		# Get all the tex from the document
		while blocks:
			block = blocks.pop(0)
			
			accumulated_tex_blocks.append(block)
			
			# Does this block also end the latex environment?
			if ("\n%s"%block).rstrip().endswith(LaTeXBlockProcessor.ENV_END):
				break
		
		latex_raw = "\n\n".join(accumulated_tex_blocks)
		latex_match = LaTeXBlockProcessor.latex_re.match(latex_raw)
		
		# Check the latex environment conforms to spec!
		if latex_match is None:
			raise Exception("Invalid latex environment:\n%s"%latex_raw)
		
		alt = latex_match.group(1)
		src = latex_match.group(2)
		img = os.path.join(self.configs["latex_img_dir"], "%s.png"%(slugify(alt, "_")))
		
		self.render_latex(src, img)
		
		# Add the image of the latex supplied
		blocks.insert(0, "![%s](file://%s)"%(alt,img))


class LaTeX(Extension):
	
	def __init__(self, configs):
		self.configs = configs
	
	def extendMarkdown(self, md, md_globals):
		md.parser.blockprocessors.add('latex', LaTeXBlockProcessor(self.configs, md.parser), '_begin')


def makeExtension(configs=None):
	return LaTeX(configs or [])

