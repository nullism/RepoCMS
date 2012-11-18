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
    
    name = 'link'
    description = 'Creates internal or external links'
    author = 'Aaron Meier'
    version = '1.0'
    usage = '[[link|path or page|<label>|<title>|<target>|<attrs>]]'
    pattern = '\[\[link\|(.*?)\]\]'
    filetype_support = ['html', 'md', 'rst','textile']
    debug = []
    
    def __init__(self, ut, pb):
        self.pb = pb
        self._conf = ut._conf
        
    def pre_filter(self, match):
        m = [m for m in match.split('|') if m.strip() != '']
        path = m[0]
        attrs = ''
        title = ''
        #label = ' '.join([w.capitalize() for w in path.split('-')])
        label = path.replace('-',' ').lower()
        target = '_self'
        if len(m) > 1 and m[1]:
            label = m[1]
        if len(m) > 2 and m[2]:
            title = m[2]
        if len(m) > 3 and m[3]:
            target = m[3]
        if len(m) > 4 and m[4]:
            attrs = m[4]
        
        if not path.startswith('/') and '://' not in path:
            path = '%s/%s/%s'%(self._conf.PATH_PREFIX, self.pb['lang'], path)
        
        link = '<a href="%s" target="%s" title="%s" %s>%s</a>'\
               %(path, target, title, attrs, label)
               
        if self.pb['filetype'] == 'rst':
            link = '`%s <%s>`_'%(label, path)
        elif self.pb['filetype'] == 'textile':
            link = ' %s'%(link)
        
        return link
        
    def post_filter(self, match):
        return match
