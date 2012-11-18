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
import re 
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class CustomFilter(object):
    
    name = 'code'
    description = 'Syntax highlights code'
    author = 'Aaron Meier'
    version = '1.0'
    usage = '[[code|<language>]] # Code goes here [[/code]]'
    pattern = '\[\[code(.*?)\]\](.*?)\[\[/code\]\]'
    filetype_support = ['html', 'md', 'rst','textile']
    
    def __init__(self, ut, pb):
        self._ut = ut
        self._conf = ut._conf
        self._db = ut._db
        self.debug = []
        self.pb = pb
    
    def pre_filter(self, args):
        slang = args[0].strip().split('|')[-1]
        if not slang:
            slang = 'text'
        code = args[1]

        self.debug.append('Highlighting block as "%s"'%(slang))
        lexer = get_lexer_by_name(slang)
        formatter = HtmlFormatter(noclasses=False)
        code = '%s'%(highlight(code, lexer, formatter))
        code = code.replace('(','&#40;')
        code = code.replace(')','&#41;')
        code = code.replace('[','&#91;')
        code = code.replace(']','&#93;')
        code = code.replace('{','&#123;')
        code = code.replace('}','&#125;')
        
        if self.pb['filetype'] == 'rst':
            code = code.split('\n')
            code = '\t'.join([l+'\n' for l in code])
            code = '\n.. raw:: html\n\n\t%s\n'%(code)
        elif self.pb['filetype'] == 'textile':
            code = code.split('\n')
            code = '&nbsp;\n'.join([l for l in code])
            code = '\nnotextile.. %s'%(code)
        return code
        
    def post_filter(self, text):
        return text
    
    
