from frozn.builder import site
jasonbartz = site.Site(root='/Users/bartz/Code/repo/blog/frozn',
            deploy_directory='/Users/bartz/Code/repo/blog-static/frozn/frozn/_deploy/', 
            site_directory='/Users/bartz/Code/repo/blog-static/frozn/frozn/_site/',
            config_file='/Users/bartz/Code/repo/blog-static/frozn/frozn/config.json',
            static_files_source='/Users/bartz/Code/repo/blog-static/frozn/frozn/static/')
jasonbartz.build()