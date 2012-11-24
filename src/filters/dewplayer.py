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
    name = 'dewplayer'
    author = 'Aaron Meier'
    version = '1.0'
    usage = '[[dewplay|mp3 file]]'
    description = 'Play MP3 files inside DewPlayer'
    pattern = r'\[\[dewplay.*?\|(.*?)\]\]'
    filetype_support = ['html', 'md', 'rst', 'textile'] 

    def __init__(self, ut, pb):
        self.pb = pb
        self.ut = ut
        self.conf = ut._conf
    
    def pre_filter(self, match):
        args = match.split('|')
        label = None
        popup = False
        player = "dewplayer-mini.swf"
        w = 160
        h = 20
        if len(args) > 1:
            args[1] = args[1].strip().lower()
            if args[1] == 'bubble':
                player = "dewplayer-bubble.swf"
                w = 250
                h = 65
            elif args[1] == 'classic':
                player = "dewplayer.swf"
                w = 200
                h = 20
            elif args[1] == 'multi':
                player = "dewplayer-multi.swf"
                w = 240
                h = 20
            elif args[1] == 'playlist':
                player = "dewplayer-playlist.swf"
                w = 240
                h = 200

        if len(args) > 2:
            args[2] = args[2].strip().lower()
            if args[2] == 'popup':
                popup = True

        if len(args) > 3:
            label = args[3].strip()

        files = [f.strip() for f in args[0].split(',')]
        if not label: 
            label = files[0]
        urls = "|".join(["%s/%s"%(self.conf.PATH_UPLOAD, u) for u in files]) 
        html = '<div class="dewplayer"> '\
               '<object type="application/x-shockwave-flash" '\
               'data="%s/dewplayer/%s" width="%s" '\
               'height="%s">'\
               '<param name="wmode" value="transparent" /> '\
               '<param name="movie" value="%s/dewplayer/%s" /> '\
               '<param name="flashvars" value="mp3=%s" /> </object></div>'\
                %(self.conf.PATH_STATIC, player, w, h, 
                  self.conf.PATH_STATIC, player, urls)
        if popup:
            html = '<a href="%s/dewplayer/dewplayer.html?mp3s=%s&amp;player=%s"'\
                   ' onclick="window.open(this.href, \'dewplayer\','\
                   ' \'height=%s, width=%s\'); return false;">%s</a>'\
                   %(self.conf.PATH_STATIC, urls, player, h+40, w+20, label)

        if self.pb['filetype'] == 'rst':
            html = "\n.. raw:: html\n\n\t%s\n"%(html)
        elif self.pb['filetype'] == 'textile':
            html = "notextile.. %s"%(html)
        return html 

    def post_filter(self, match):
        return match
