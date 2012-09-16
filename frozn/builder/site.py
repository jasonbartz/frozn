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
from frozn.builder.extensions import CodeBlock

from jinja2.ext import AutoEscapeExtension



class FroznBase(object):
    '''
    Frozn base class
    bartz_root = /Users/bartz/Code/repo/blog
    '''
    def __init__(self,
                root=None,
                site_directory='frozn/_deploy/',
                static_files_source='frozn/static/',
                posts_directory='frozn/site/posts/',
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

        # Set Frozn specific variables
        #   These are very explicit, if not set, app will fail to work

        self.site_directory = '%s/%s' % (root, site_directory)

        self.static_files_source = '%s/%s' % (root, static_files_source)

        self.posts_directory = '%s/%s' % (root, posts_directory)

        self.templates_directory ='%s/%s' % (root, templates_directory)

        self.static_directory = static_directory


class Site(FroznBase):

    def build(self):
        '''
        Method that compiles that site,
            prints out html, css, js and folder directories
        '''
        # Clear old site
        self._reset()
        # Set environments
        site_env = Environment(loader=PackageLoader('frozn','.'), extensions=[CodeBlock])

        # Build Posts

        posts_list = os.listdir(self.posts_directory)

        # Sort Posts in descending order by date
        posts_list = sorted(posts_list, reverse=True)

        post_templates = []

        for post in posts_list:
            post_template = {}

            post_date, post_name = post.split('_')

            post_template['template'] = site_env.get_template('site/posts/%s' % post)
            post_template['name'] = post_name
            post_template['date'] = post_date
            print post_date
            post_templates.append(post_template)


        # Render Latest Post


        # Build Templates
        template = site_env.get_template('templates/home.html')

        # Move Posts to _deploy directory
        for post in post_templates:
            with open('%sposts/%s' %(self.site_directory,post['name']), 'wb') as write_post:
                post_base = site_env.get_template('templates/post_detail.html')
                rendered_post = post['template'].render()
                write_post.write(post_base.render(post=rendered_post))

        # Move Home to _deploy directory
        with open('%s/index.html' % self.site_directory, 'wb') as write_home:
            latest_post = post_templates[0]['template'].render()
            write_home.write(template.render(latest_post=latest_post))

        # Move static to _deploy directory
        shutil.copytree(self.static_files_source, '%s/%s' % (self.site_directory,self.static_directory))

    def _reset(self):
        try:
            shutil.rmtree(self.site_directory)
        except OSError, e:
            print e
        os.makedirs(self.site_directory)
        os.makedirs('%s/posts' % self.site_directory)

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

        with open('%s%s.html' % (self.posts_directory, filename), 'wb') as post_write:
            post_write.write(post)