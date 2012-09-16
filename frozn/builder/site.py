'''
Build the site
'''
# Standard Library
import os
import shutil
import json
import cStringIO

# Third Party
from jinja2 import Environment, PackageLoader, ChoiceLoader, FileSystemLoader

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
                **kwargs):
        '''
        Initializes all Frozn classes

        Required Param
        :: root
        Root directory where your app lives

        Optional Params
        :: deploy_directory
        Where to render the deployable static files

        :: static_files_source
        Where the static files (js/css) are stored

        :: site_directory
        Where the site information, posts/pages, are stored

        :: templates_directory
        Where the jinja templates are stored
        '''
        # Set initial args and kwargs

        initial_kwargs = {
            'deploy_directory': '%s/_deploy/' % root,
            'static_files_source': '%s/static/' % root,
            'site_directory': '%s/site/' % root,
            'templates_directory': '%s/templates/' % root,
            'static_directory': 'static',
            'config_file': '%s/config.json' % root,
        }
        initial_kwargs.update(kwargs)
        for key, value in initial_kwargs.iteritems():
            setattr(self, key, value)

        if not root:
            raise NoRootDirectory('Please pass a root directory to the class instantiation as keyword "root"')
        else:
            self.root = root

class Site(FroznBase):

    def _load_config(self):
        '''
        Loads external config files
        '''
        with open(self.config_file,'rb') as open_config_object:
            self.configuration = json.loads(open_config_object.read())

        for config_item in self.configuration['frozn-config']:
            for key, value in config_item.iteritems():
                setattr(self, key, value)


    def _initialize_environment(self):
        '''
        Resets directories and initializes jinja template environment
        '''
        # Clear old site
        Directory.reset_deploy_directory(self.deploy_directory)

        # Load both the main template environement
        #   And the site directory as locations
        #   for frozn to look for templates
        self.deploy_env = Environment(
            loader = ChoiceLoader([
                PackageLoader('frozn','.'),
                FileSystemLoader(self.site_directory),
            ]),extensions=[CodeBlock, MarkDown])

        # Add configuration variables to the template globals
        self.deploy_env.globals.update({
            'name': self.name,
            'nav_list': self.links,
            'javascript': self.javascript,
            'css': self.css,
        })

    def _get_content(self):
        '''
        Retrieve blog posts and pages from the posts template directory (site_directory)
        '''
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
            post_template['template'] = self.deploy_env.get_template('posts/%s' % post)
            post_template['name'] = post_name
            post_template['date'] = post_date

            print(post_date)
            post_templates.append(post_template)

            self.post_templates = post_templates

    def _render(self):
        '''
        Render posts, pages and static files to the deploy_directory
        #! Refactoring in v0.0.4
        '''
        # Move Posts to _deploy directory
        for post in self.post_templates:
            # Create directory for post to live inside.
            #   This is so you can link without the .html
            post_object = cStringIO.StringIO()
            post_base = self.deploy_env.get_template('templates/post_detail.html')
            rendered_post = post['template'].render()
            post_object.write(post_base.render(post=rendered_post))
            post['rendered'] = post_object

        # Render home
        home_object = cStringIO.StringIO()
        latest_post = self.post_templates[0]['template'].render()
        home = self.deploy_env.get_template('templates/home.html')
        home_object.write(home.render(latest_post=latest_post,
                                    latest_posts_list=self.post_templates[:5]))
        self.home_object = home_object

        # Create archive page
        archive_object = cStringIO.StringIO()
        archive = self.deploy_env.get_template('templates/archive.html')
        archive_object.write(archive.render(post_list=self.post_templates))
        self.archive_object = archive_object

    def _write(self):
        '''
        Write the rendered files to the deploy directory
        '''
        # Write Posts
        for post in self.post_templates:
            post_directory = '%sposts/%s' % (self.deploy_directory, post['name'])
            self._write_file(post['rendered'], post_directory)

        # Write Pages

        # Write Archive
        archive_directory = '%s/archives' % (self.deploy_directory)
        self._write_file(self.archive_object, archive_directory)

        # Write Home
        self._write_file(self.home_object, self.deploy_directory)

        # Static
        shutil.copytree(self.static_files_source, '%s/%s' % (self.deploy_directory,self.static_directory))

    def _write_file(self, file_object, directory):
        '''
        Write an individual file to a directory
        '''
        try:
            os.makedirs(directory)
        except OSError, e:
            print e

        with open('%s/index.html' % directory, 'wb') as f_input:
            f_input.write(file_object.getvalue())

    def build(self):
        '''
        Method that compiles that site,
            prints out html, css, js and folder directories
        '''
        self._load_config()
        self._initialize_environment()
        self._get_content()
        self._render()
        self._write()

class Create(FroznBase):
    '''
    Class to create Posts and Pages
    #! Refactoring in v0.0.4
    '''
    def post(self,
            headline,
            year,
            month,
            day,
            post_time=None):

        # Open past_base template
        with open('%spost_base.html' % self.templates_directory, 'rb') as post_base:
            post_base_string = post_base.read()

        # Add datetime and headline vars

        post_datetime = '%s-%s-%s' % (year, month, day)
        if post_time:
            post_datetime = post_datetime + post_time

        post = post_base_string % (headline, post_datetime)

        filename = '%s_%s' % (post_datetime, slugify(headline))

        # Print template to site_directory
        with open('%sposts/%s' % (self.site_directory, filename), 'wb') as post_write:
            post_write.write(post)

    #! Coming soon
    # def page(self,
    #         title,
    #         year,
    #         month,
    #         day,
    #         page_time=None):

class Directory(object):
    '''
    A helper class to manage directories for the app.
        Creates directory trees.
    '''
    @staticmethod
    def reset_deploy_directory(deploy_directory):
        # Remove current deploy directory
        try:
            shutil.rmtree(deploy_directory)
        except OSError, e:
            print e
        # Make dirs needed for deployment
        os.makedirs(deploy_directory)
        os.makedirs('%s/posts' % deploy_directory)
