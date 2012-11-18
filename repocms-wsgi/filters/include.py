
class CustomFilter(object):
    
    name = 'include'
    version = '1.0'
    author = 'Aaron Meier'
    description = 'Include pages'
    usage = '[[include|<page name>]]'
    pattern = '\[\[include\|(.*?)\]\]'
    filetype_support = ['html','md','rst','textile']
    debug = []

    def __init__(self, ut, pb):
        self.pb = pb

    def pre_filter(self, match):
        match = '<div class="include">'\
                '{%% include "%s__%s.html" %%}</div>'\
                %(self.pb['lang'], match) 

        if self.pb['filetype'] == 'rst':
            match = '\n.. raw:: html\n\n\t%s\n'\
                    %(match)
        elif self.pb['filetype'] == 'textile':
            match = 'notextile.. %s'%(match)    

        return match

    def post_filter(self, match):
        return match
