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

    name = 'textreverse'
    version = '1.0.1'
    author = 'Aaron Meier'
    description = 'Reverses strings'
    usage = '[[textreverse]] String to be reversed [[/textreverse]]'
    pattern = '\[\[\s?textreverse\s?\]\](.*?)\[\[\s?/textreverse\s?\]\]'
    filetype_support = ['html','md','rst','textile']
    debug = []

    def __init__(self, ut, pb):
        self._ut = ut
        self._db = ut._db
        self._conf = ut._conf

    def pre_filter(self, match):
        self.debug.append('Found match: %s'%(match))
        return match[::-1].strip()

    def post_filter(self, match):
        return match
