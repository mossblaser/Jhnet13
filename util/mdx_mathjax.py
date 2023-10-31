

import markdown
import xml.etree.ElementTree as etree

class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node

class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals={}):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.register(
            MathJaxPattern(),
            'mathjax',
            md.inlinePatterns.get_index_for_name("escape") + 1
        )

def makeExtension(**kwargs):
    return MathJaxExtension(**kwargs)


