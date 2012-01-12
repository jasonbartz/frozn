from jinja2 import nodes
from jinja2.ext import Extension

class CodeBlock(Extension):
    # a set of names that trigger the extension.
    tags = set(['codeblock'])

    def __init__(self, environment):
        super(CodeBlock, self).__init__(environment)

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # we only listen to ``'cache'`` so this will be a name token with
        # `cache` as value.  We get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = parser.stream.next().lineno


        # now we parse the body of the cache block up to `endcache` and
        # drop the needle (which would always be `endcache` in that case)
        body = parser.parse_statements(['name:endcodeblock'], drop_needle=True)
        
        body[0].nodes[0].data
        
        codeblock_string = '''<div class="codeblock">
                                    <pre class="prettyprint">
                                        %s
                                    </pre>
                              </div>
                    ''' % body[0].nodes[0].data
        body[0].nodes[0].data = codeblock_string
        
        # now return a `CallBlock` node that calls our _cache_support
        # helper method on this extension.
        return nodes.Block('codeblock',body,[]).set_lineno(lineno) 
                