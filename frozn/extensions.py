from jinja2 import nodes
from jinja2.ext import Extension
import markdown

CODEBLOCK_STRING = \
'''<div class="codeblock">
        <pre class="prettyprint">
            %s
       </pre>
   </div>'''

class CodeBlock(Extension):
    '''
    A repeatable tag for adding codeblocks that will be syntax-highlighted inside templates
    '''
    tags = set(['codeblock'])

    def parse(self, parser):
        node = nodes.Scope(lineno=next(parser.stream).lineno)
        node.body = parser.parse_statements(('name:endcodeblock',),drop_needle=True)
        codeblock_string = CODEBLOCK_STRING % node.body[0].nodes[0].data
        node.body[0].nodes[0].data = codeblock_string
        
        return node
        
class MarkDown(Extension):
    '''
    A non-repeatable tag that makes use of the markdown library for converting writing to HTML
    '''
    tags = set(['markdown'])
    
    def parse(self, parser):
        node = nodes.Scope(lineno=next(parser.stream).lineno)
        # Set the node body
        node.body = parser.parse_statements(('name:markdown',), drop_needle=True)
        
        # Loop through the body, ignoring CodeBlocks
        # Transform the body into Markdown
        for body_object in node.body:
            # Conform body to markdown
            try:
                body_object.nodes[0].data = markdown.markdown(body_object.nodes[0].data)
            # Other objects, like CodeBlock, will trigger this exception
            except AttributeError:
                pass
                
        return node