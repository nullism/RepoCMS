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
import os
from lxml.html import etree

class CustomFilter(object):
    
    name = 'tableofcontents'
    description = 'Generates table of contents from html headings'
    author = 'Aaron Meier'
    version = '1.2'
    usage = '[[toc|<Title>]]'
    pattern = '(\[\[\s?toc.*?\]\])(.*)'
    filetype_support = ['html', 'md', 'rst','textile']
    
    
    def __init__(self, ut, pb):
        self._ut = ut
        self._conf = ut._conf
        self._db = ut._db
        self.debug = []
        self.pb = pb
    
    def pre_filter(self, match):
        result = match[0]+match[1]

        if self.pb['filetype'] == 'md':
            # Wrap TOC in <div> to protect against MarkDown
            result = match[0].replace(match[0],
                        '<div>%s</div>'%(match[0])) + match[1]

        elif self.pb['filetype'] == 'rst':
            # Place TOC in raw HTML to protect against RST
            result_a = match[0].replace(match[0],
                       '.. raw:: html\n\n\t<div>%s</div>\n'\
                       %(match[0]))
            result = result_a + match[1]

        elif self.pb['filetype'] == 'textile':
            # Place TOC in raw HTML to protect agaist Textile
            result = match[0].replace(match[0],
                     '\nnotextile.. <div>%s</div>\n'\
                     %(match[0])) + match[1]
            
        return result
        
    def post_filter(self, args):
       
        title = args[0].split('[[')[-1].split(']]')[0].split('|')[-1]
        if title.strip():
            title = title.strip()

        text = args[1]
        counts = {}
        doc = etree.fromstring(text, etree.HTMLParser())
        hids = []            
        toc_html = '<div id="toc" class="table_of_contents"><h3>%s</h3>\n'%(title)
        for node in doc.xpath('//h1|//h2|//h3|//h4|//h5'):
            if node.tag.lower() == 'h1':
                this_depth = 0
            elif node.tag.lower() == 'h2':
                this_depth = 1
            elif node.tag.lower() == 'h3':
                this_depth = 2
            elif node.tag.lower() == 'h4':
                this_depth = 3
            elif node.tag.lower() == 'h5':
                this_depth = 4
            else:
                continue
            
            p = re.compile('[^a-zA-Z0-9\s\_]')
            this_id = re.sub(p, '-', node.text).replace(' ','-')
            if this_id in hids:
                counts[this_id] = counts.get(this_id, 0) + 1
                this_id = '%s-%s'%(this_id, counts[this_id])
            hids.append(this_id)           
            
            pat = '%s'%(etree.tostring(node))
            rep = '<%s id="%s" class="toc_heading">%s'\
                  '<span class="toc_top"><a href="#toc">top</a></span></%s>'\
                  '<p style="clear: both;"></p>'\
                  %(node.tag, this_id, node.text, node.tag)
            text = text.replace(pat, rep, 1)
            indent_px = this_depth * 20
            toc_html += '<p style="margin-left: %spx">+ '\
                        '<a href="#%s">%s</a></p>\n'\
                        %(indent_px, this_id, node.text)                

        toc_html += '</div>\n'
        text = text.replace(text,toc_html+text)
        return text
