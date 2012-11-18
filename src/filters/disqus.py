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
    
    name = 'disqus'
    description = 'Embeds disqus comments'
    author = 'Aaron Meier'
    version = '1.1.5'
    usage = '[[disqus|<sitename>]]'
    pattern = '\[\[disqus(.*?)\]\]'
    filetype_support = ['html', 'md', 'rst', 'textile']
    default_sitename = 'repocms'
    debug = []

    def __init__(self, ut, pb):
        self._ut = ut
        self.pb = pb

    def pre_filter(self, match):
        
        sitename = self.default_sitename
        args = [a.strip() for a in match.split('|') if a.strip() != '']
        if args[0]:
            sitename = args[0]
            
        html = '''<div id="disqus">
       <div id="disqus_thread"></div>
       <script type="text/javascript">
            var disqus_shortname = '%s';
            (function() {
                var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
                (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
            })();
        </script>
        <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
        <a href="http://disqus.com" class="dsq-brlink">comments powered by <span class="logo-disqus">Disqus</span></a>
    </div>
    '''%(sitename)
    
        if self.pb['filetype'] == 'rst':
            html = '.. raw:: html\n\n\t%s\n'%(html)
        elif self.pb['filetype'] == 'textile':
            html = 'notextile.. %s'%(html)
            
        return html
        
    def post_filter(self, match):
        return match
