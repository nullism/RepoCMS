"""
   Copyright 2012 Aaron Meier

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
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
