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
    
    name = 'youtube'
    description = 'Embeds YouTube videos'
    author = 'Aaron Meier'
    version = '1.0'
    usage = '[[youtube|url|<width>|<height>]]'
    pattern = '\[\[youtube\|(.*?)\]\]'
    filetype_support = ['html', 'md', 'rst','textile']
    debug = []
    
    def __init__(self, ut, pb):
        self._ut = ut
        self.pb = pb
        
    def pre_filter(self, match):
        args = [m.strip() for m in match.split('|')]
        url = args[0]
        
        if 'youtu' not in url:
            url = 'http://www.youtube.com/embed/%s'%(url)
            
        width = 560
        height = 315
        if len(args) > 1:
            width = args[1]
        elif len(args) > 2:
            height = args[2]
        
        html = '<iframe <iframe width="%s" height="%s" '\
               'src="%s" frameborder="0" allowfullscreen></iframe>'\
               %(width, height, url)
            
        if self.pb['filetype'] == 'rst':
            html = '.. raw:: html\n\n\t%s\n'%(html)
        elif self.pb['filetype'] == 'textile':
            html = 'notextile.. %s'%(html)
        
        return html
        
    def post_filter(self, match):
        return match
