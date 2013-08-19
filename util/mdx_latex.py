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

If the alt-text given is "<preamble>", the code is not rendered but added to the
preamble of all succeeding latex blocks.

The PNG file will be placed in the directory configs["latex_img_dir"].
"""

from markdown.blockprocessors import BlockProcessor
from markdown.extensions      import Extension

from markdown.extensions.headerid import slugify

from mako.template import Template

from subprocess import Popen

from PIL import Image, PngImagePlugin

import hashlib

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
		\documentclass[border=0pt,12pt]{standalone}
		
		\usepackage{amsmath}
		\usepackage{amssymb}
		
		\usepackage{graphicx}
		
		\usepackage{ifthen}
		
		\usepackage[outline]{contour}
		\contourlength{1.5pt}
		
		\usepackage{tikz}
		\usepackage{tikz3d}
		\usetikzlibrary{ hexagon
		               , calc
		               , backgrounds
		               , positioning
		               , decorations.pathreplacing
		               , decorations.markings
		               , arrows
		               , positioning
		               , automata
		               , shadows
		               , fit
		               , shapes
		               , arrows
		               }
		
		${preamble}
		
		\begin{document}
			${document}
		\end{document}
	""")
	
	
	def __init__(self, configs, *args, **kwargs):
		self.configs = dict(configs)
		BlockProcessor.__init__(self, *args, **kwargs)
		
		# LaTeX preamble
		self.preamble = ""
	
	
	def set_png_metadata(self, png_filename, metadata):
		"""
		Takes a PNG filename and overwrites the fields specified in metadata with
		the values given, adding any new fields.
		"""
		im = Image.open(png_filename)
		
		# This hack works-around PIL's broken png metadata support. Disovered here:
		# http://blog.client9.com/2007/08/python-pil-and-png-metadata-take-2.html
		meta = PngImagePlugin.PngInfo()
		
		# These meta-data entries are added (eroneously) by PIL, ignore them
		reserved = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect')
		
		# Add in the new metadata
		img_metadata = im.info.copy()
		img_metadata.update(metadata)
		
		# Add to the PNG
		for k,v in img_metadata.iteritems():
			if k not in reserved:
				meta.add_text(k,v)
		
		# Write it out
		im.save(png_filename, pnginfo=meta)
	
	
	def get_png_metadata(self, png_filename):
		"""
		Takes a PNG filename and returns the metadata fields it contains as a dict.
		"""
		return Image.open(png_filename).info.copy()
	
	
	def render_latex(self, latex_snippet, output_png_file, output_pdf_file):
		"""
		Takes a snippet of latex and produces a png at the filename specified. This
		method is lazy, if the tex has not changed since the last run, it is not
		compiled. This is detected by checking a hash of the tex added to the PNG
		metadata.
		"""
		tmp_dir = tempfile.mkdtemp(prefix = "mdx_latex_")
		tex_file = os.path.join(tmp_dir, "file.tex")
		pdf_file = os.path.join(tmp_dir, "file.pdf")
		
		try:
			# Generate the tex file
			tex = LaTeXBlockProcessor.LATEX_TEMPLATE.render(
				preamble = self.preamble,
				document = latex_snippet,
			)
			tex_hash = hashlib.sha1(tex).hexdigest()
			
			# Check if anything needs to be done
			try:
				png_meta = self.get_png_metadata(output_png_file)
				if tex_hash == png_meta.get("tex_hash", None):
					# Already got the latest version in the PNG, do nothing!
					return
			except IOError:
				# No file exists yet so we definately should build it
				pass
			
			
			# Store the tex in a file to be compiled
			with open(tex_file, "w") as f:
				f.write(tex)
			
			# Try and build the file
			for build_num in range(LaTeXBlockProcessor.LATEX_BUILDS):
				p = Popen( [ "pdflatex"
				           , "-shell-escape"
				           , "-halt-on-error"
				           , "-output-directory", tmp_dir
				           , tex_file]
				         , cwd    = os.path.realpath(self.configs.get("input_path", "./"))
				         , stdin  = None
				         , stdout = sys.stderr
				         , stderr = sys.stderr
				         )
				if p.wait() != 0:
					raise Exception("LaTeX Compilation Failed for:\n%s"%latex_snippet)
			
			# Make a copy of required
			if output_pdf_file is not None:
				shutil.copy(pdf_file, output_pdf_file)
			
			# Convert to PNG
			p = Popen( ["convert", "-density", "440", pdf_file, "-resize", "25%", output_png_file]
			         , stdin  = None
			         , stdout = sys.stderr
			         , stderr = sys.stderr
			         )
			if p.wait() != 0:
				raise Exception("Converting PDF to PNG failed for:\n%s"%latex_snippet)
			
			# Add the hash of the source to the metadata 
			self.set_png_metadata(output_png_file, {"tex_hash":tex_hash})
			
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
		
		# Check to see if this is a block defining the preamble for latex blocks in
		# this document.
		if alt == "<preamble>":
			# For the preamble section
			self.preamble += src
		else:
			# A Normal LaTeX file to render
			
			# Make the image a link to the PDF?
			link_pdf = False
			if "--pdf" in alt:
				alt = alt.replace("--pdf", "").strip()
				link_pdf = True
				
			
			img = os.path.join(self.configs["latex_img_dir"], "%s.png"%(slugify(alt, "_")))
			
			if link_pdf:
				pdf = os.path.join(self.configs["latex_img_dir"], "%s.pdf"%(slugify(alt, "_")))
			else:
				pdf = None
			
			self.render_latex(src, img, pdf)
			
			# Add the image of the latex supplied
			if link_pdf:
				blocks.insert(0, "[![%s](file://%s)](file://%s)"%(alt,img,pdf))
			else:
				blocks.insert(0, "![%s](file://%s)"%(alt,img))


class LaTeX(Extension):
	
	def __init__(self, configs):
		self.configs = configs
	
	def extendMarkdown(self, md, md_globals):
		md.parser.blockprocessors.add('latex', LaTeXBlockProcessor(self.configs, md.parser), '_begin')


def makeExtension(configs=None):
	return LaTeX(configs or [])

