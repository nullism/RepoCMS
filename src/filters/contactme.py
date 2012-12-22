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

    name = 'contactme'
    description = 'Embeds a ContactMe.com form'
    author = 'Aaron Meier'
    version = '1.0'
    usage = '[[contactme|formid|<width>|<height>]]'
    pattern = '\[\[\s?contactme\|(.*?)\]\]'
    filetype_support = ['html', 'md', 'rst','textile']

    def __init__(self, ut, pb):
        self.pb = pb
        self.ut = ut

    def pre_filter(self, match):
        args = [a.strip() for a in match.split('|')]

        form_id = args[0]
        width = '510px'
        height = '500px'

        if len(args) > 1 and args[1] != '':
            width = args[1]
        if len(args) > 2 and args[2] != '':
            height = args[2]

        html = '<iframe src="http://contactme.com/%(form_id)s/embed"'\
               ' frameborder="0" scrolling="no" allowtransparency="true"'\
               ' style="height: %(height)s; width: %(width)s;">'\
               '</iframe>'\
               %({'form_id':form_id, 'height':height, 'width':width})

        if self.pb['filetype'] == 'rst':
            html = '\n.. raw:: html\n\n\t%s\n'%(html)
        elif self.pb['filetype'] == 'textile':
            html = 'notextile.. %s\n'%(html)

        return html

    def post_filter(self, match):
        return match
