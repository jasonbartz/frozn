'''
Build the site
'''
# Standard Library
import os
import shutil

# Third Party
from jinja2 import Environment, PackageLoader

# Local Library
from frozn.builder.utils import slugify
from frozn.builder.exceptions import NoRootDirectory
from frozn.builder.extensions import CodeBlock, MarkDown


class FroznBase(object):
    '''
    Frozn base class
    '''
    def __init__(self,
                root=None,
                deploy_directory='frozn/_deploy/',
                static_files_source='frozn/static/',
                site_directory='frozn/_site/',
                templates_directory='frozn/templates/',
                static_directory='static',
                *args,
                **kwargs):
        '''
        Initializes all Frozn classes
        
        Required Param(s)
        :: root
        Root directory where your app lives
            !! For now, you must pass in the root app directory when the class is initialized.
            !! Will be changed in later version, need to explore os more
        
        Optional Params
            !! Coming in next version
        '''
        # Set initial args and kwargs
        self.args = args
        self.kwargs = kwargs
        if not root:
            raise NoRootDirectory('Please pass a root directory to the class instantiation as keyword "root"')
        else:
            self.root = root
        # Set Frozn specific variables
        #   These are very explicit, if not set, app will fail to work
        
        self.deploy_directory = '%s/%s' % (root, deploy_directory)
        
        self.static_files_source = '%s/%s' % (root, static_files_source)
        
        self.site_directory = '%s/%s' % (root, site_directory)
        
        self.templates_directory ='%s/%s' % (root, templates_directory)

        self.static_directory = static_directory
        

class Site(FroznBase):
        
    def _initialize_environment(self):
        # Clear old site
        manager = Directory(root=self.root)
        manager.reset_deploy_directory()
        
        # Set environments
        self.deploy_env = Environment(loader=PackageLoader('frozn','.'), extensions=[CodeBlock, MarkDown])
        
    def _get_posts(self):
        
        # Build Posts
        posts_list = os.listdir('%sposts/' % self.site_directory)
        
        # Sort Posts in descending order by date
        posts_list = sorted(posts_list, reverse=True)
        
        # Create blank list to store template objcts
        post_templates = []
        
        # Iterate through list of posts
        for post in posts_list:
            # Create a blank dict to store information about the post
            post_template = {}
            
            # Split the name of the post based on underbar
            post_date, post_name = post.split('_')
            
            # Add post and metadata to dict
            post_template['template'] = self.deploy_env.get_template('/_site/posts/%s' % post)
            post_template['name'] = post_name
            post_template['date'] = post_date
            
            print(post_date)
            post_templates.append(post_template)
        
            self.post_templates = post_templates
        
    def _render(self):
        # Move Posts to _deploy directory
        for post in self.post_templates:
            # Create directory for post to live inside.
            #   This is so you can link without the .html
            
            post_directory = '%sposts/%s' % (self.deploy_directory, post['name'])
            
            os.makedirs(post_directory)
            with open('%s/index.html' % post_directory, 'wb') as write_post:
                post_base = self.deploy_env.get_template('templates/post_detail.html')
                rendered_post = post['template'].render()
                write_post.write(post_base.render(post=rendered_post))
        
        # Move Home to _deploy directory
        with open('%s/index.html' % self.deploy_directory, 'wb') as write_home:
            latest_post = self.post_templates[0]['template'].render()
            home = self.deploy_env.get_template('templates/home.html')
            write_home.write(home.render(latest_post=latest_post,
                                        latest_posts_list=self.post_templates[:5]))
        
        # Create archive page
        archive_directory = '%sarchives' % (self.deploy_directory)
        os.makedirs(archive_directory)
        with open('%s/index.html' % archive_directory, 'wb') as write_archive:
            archive = self.deploy_env.get_template('templates/archive.html')
            write_archive.write(archive.render(post_list=self.post_templates))
        
        # Move static to _deploy directory
        shutil.copytree(self.static_files_source, '%s/%s' % (self.deploy_directory,self.static_directory))
        
    def build(self):
        '''
        Method that compiles that site,
            prints out html, css, js and folder directories
        '''
        self._initialize_environment()
        self._get_posts()
        self._render()
        
class Post(FroznBase):
    
    def post(self,
            headline,
            year,
            month,
            day,
            post_time=None):

        with open('%spost_base.html' % self.templates_directory, 'rb') as post_base:
            post_base_string = post_base.read()
            
        post_datetime = '%s-%s-%s' % (year, month, day)
        if post_time:
            post_datetime = post_datetime + post_time
        
        post = post_base_string % (headline, post_datetime)
        
        filename = '%s_%s' % (post_datetime, slugify(headline))
        
        with open('%sposts/%s' % (self.site_directory, filename), 'wb') as post_write:
            post_write.write(post)
            
class Directory(FroznBase):
    '''
    A helper class to manage directories for the app.
        Creates directory trees.
    '''
    def reset_deploy_directory(self):
        try:
            shutil.rmtree(self.deploy_directory)
        except OSError, e:
            print e
        os.makedirs(self.deploy_directory)
        os.makedirs('%s/posts' % self.deploy_directory)
        
    