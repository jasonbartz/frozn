'''
Build the site
'''

class Site(object):
    
    def __init__(self,
                *args,
                **kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def build_site(self):
        '''
        Method that compiles that site,
            prints out html, css, js and folder directories
        '''
        pass