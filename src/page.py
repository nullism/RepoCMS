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
import sys, time, json, os, re, random
from PIL import Image, ImageOps
from math import ceil, floor
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"./lib/"))
if path not in sys.path:
    sys.path.insert(0,path)
from handler import Handler
from utility import Utility

class Page(Handler):
    
    def __init__(self,env):
        Handler.__init__(self, env)
        self._ut = Utility()
        self._conf = self._ut._conf
        self._db = self._ut._db
        self._jtheme = self._ut._jtheme
        self._jtheme_mobile = self._ut._jtheme_mobile
        self._jcache = self._ut._jcache
        self._errors = []
        self._messages = []
        self._news = []
        self._page = {}
        self._site = {}
        self._ = self._ut._
        self._site['title'] = self._conf.SITE_TITLE
        self._lang = self._conf.DEFAULT_LANG
        self._template_add = {}
        self._is_mobile = self.get_is_mobile()

    
    ##
    # Handle internal redirect
    #
    def handle_redirect(self, path):
        msgs = None
        errs = None
        
        if '?' not in path: 
            path = '%s?rdr=1'%(path)
            
        if self._messages:
            msgs = self.urlencode(',,,'.join(self._messages))
            path = '%s&msgs=%s'%(path, msgs)
            
        if self._errors:
            errs = self.urlencode(',,,'.join(self._errors))
            path = '%s&errs=%s'%(path, errs)

        url = '%s%s/%s'\
              %(self._conf.PATH_WEBHOST,
                self._conf.PATH_PREFIX,
                path)
        return self.redirect(url)

    
    ##
    # Route the request to the passed function
    #
    def handle_request(self, path_defs):
        if self._conf.MAINTENANCE:
            return self.html_maintenance()
        
        msgs = self.REQ('msgs')
        if msgs:
            msgs = self.urldecode(msgs).split(',,,')
            self._messages.extend(msgs)
            
        errs = self.REQ('errs')
        if errs:
            errs = self.urldecode(errs).split(',,,')
            self._errors.extend(errs)
                        
        out = super(Page, self).handle_request(path_defs)
        if self._db._errors:
            self.weblog_errors(self._db._errors)
        if self._ut._errors:
            self.weblog_errors(self._ut._errors)
        return out

    
    ##
    # HTML: Index
    # 
    def html_index(self, lang_key=None):
        if not lang_key:
            lang_key = self._conf.DEFAULT_LANG
        page_key = self._conf.DEFAULT_PAGE
        return self.html_page(lang_key, page_key)
        
   
    ##
    # HTML: Page
    #
    def html_page(self, lang_key, page_key):
        self._lang = lang_key
        page_key = page_key.replace('/','')
        page_file = '%s__%s.html'%(lang_key, page_key)
        page_d = self._db.get_page_by_key_lang(page_key, lang_key)
        if not page_d:
            return self.template_404()
        if page_d.get('page_redirect'):
            self._messages.append(self._('Redirected from ')\
                                  +'<strong>%s</strong>'\
                                  %(page_d['page_title']))
            return self.handle_redirect(page_d['page_redirect'])
        self._page['title'] = page_d.get('page_title')
        self._page['modified'] = page_d.get('page_modified')
        self._page['lang'] = page_d.get('lang_key')
        self._page['keywords'] = page_d.get('page_keywords',[])
        try:
            self._page['content'] = self._jcache.get_template(page_file).render(
                                path_static=self._conf.PATH_STATIC,
                                path_prefix=self._conf.PATH_PREFIX,
                                path_webhost=self._conf.PATH_WEBHOST,
                                path_current=self._path,
                                theme_data=self._ut._theme_data,
                                )
            
            return self.template('page.html')
        except(Exception),e:
            return self.template_404()
    

    ##
    # HTML: Page List
    #
    def html_page_list(self, lang_key, list_type, arg, start=0, limit=25):
        self._lang = lang_key
        try:
            start = int(start)
            limit = int(limit)
        except:
            return self.template_404()

        results = []
        total = 0
        arg = self.urldecode(arg)
        keywords = []

        if list_type == 'keyword':
            keywords = self._db.get_keywords_by_lang(lang_key)
            results = self._db.get_pages_by_keyword(arg, start, limit)
            total = self._db.get_pages_by_keyword_total(arg)
    
        
        self._template_add['keywords'] = keywords 
        self._template_add['arg'] = arg
        self._template_add['results'] = results
        self._template_add['list_type'] = list_type
        self._template_add['pager'] = {'start':start,
                                       'limit':limit,
                                       'total':total,
                                       'pages':int(ceil(float(total)/limit)),
                                       'page':int(ceil(float(start)/limit))+1}
        return self.template('pagelist.html')
        
            
    ##
    # HTML: Search
    #
    def html_search(self, lang, start=0, limit=25):
        self._lang = lang
        try:
            start = int(start)
            limit = int(limit)
        except:
            return self.template_404()
            
        if not self.REQ('search'):
            return self.template('search.html')
        
        if self._method == 'POST':
            search = self.POST('search')
        else: 
            search = self.urldecode(self.GET('search'))
            
        if len(search) < 3:
            self._errors.append('Search query must be at least 3 characters')
            return self.template('search.html')
        
        results = self._db.get_pages_by_search(search, start, limit)
        total = self._db.get_pages_by_search_total(search)
        for r in results:
            ss = search.split()
            for s in ss: 
                r['page_text'] = r['page_text'].replace(s, '<strong>%s</strong>'%(s))
                
        self._template_add['results'] = results
        self._template_add['search'] = search
        self._template_add['search_encoded'] = self.urlencode(search)
        self._template_add['pager'] = {'start':start,
                                       'limit':limit,
                                       'total':total,
                                       'pages':int(ceil(float(total)/limit)),
                                       'page':int(ceil(float(start)/limit))+1}
                                       
        return self.template('search.html')
        
   
    ##
    # JTemplate
    #
    def jtemplate(self,payload=None):
        if not self._errors:
            self._errors = None
        if not self._messages:
            self._messages = None
        data = { "errors":self._errors,
                 "messages":self._messages,
                 "data":payload }
        return json.dumps(data)
        
 
    ##
    # Wrapper for get template
    #
    def template(self,f):        
        try:
            menu = self.template_menu()
        except(Exception),e:
            menu = 'Could not load menu for language "%s"'%(self._lang)
            
        try:
            if self._is_mobile:
                tpl = self._jtheme_mobile.get_template(f)
            else:
                tpl = self._jtheme.get_template(f)
        except(Exception),e:
            self._errors.append('Template Error: %s'%(e))
            return self.template_404()
            
        return tpl.render( path_static=self._conf.PATH_STATIC,
                        path_prefix=self._conf.PATH_PREFIX,
                        path_webhost=self._conf.PATH_WEBHOST,
                        path_current=self._path,
                        theme_data=self._ut._theme_data,
                        _ = self._,
                        lang=self._lang,
                        menu=menu,
                        page=self._page,
                        site=self._site,
                        add=self._template_add,
                        errors=self._errors,
                        messages=self._messages,
                        news=self._news,
                        db=self._db)

    ##
    # Template: 404
    #
    def template_404(self):
        self.set_status(404)
        return self.template('body-404.html')
        

    ##
    # Template menu
    #
    def template_menu(self):
        if self._is_mobile:
            menu = self._jcache.get_template(
                    'special/%s__menu-mobile.html'\
                    %(self._lang)).render()   
        else:
            menu = self._jcache.get_template(
                    'special/%s__menu.html'\
                    %(self._lang)).render()   
            
        return menu  

 
    ##
    # Weblog: Audit
    #
    def weblog_audit(self, messages=[]):
        if not messages:
            messages = self._messages
        user_email = None
        
        d = { 'log_type':'audit',
              'log_path':self._path,
              'log_ip':self._remote_addr,
              'user_email':user_email,
              'log_text':messages }
              
        return self._db.add_log_entry(d)
        
        
        
    ##
    # Weblog: Errors
    #
    def weblog_errors(self, errors=[]):
        if not errors:
            errors = self._errors
        user_email = None
           
        d = { 'log_type':'error',
              'log_path':self._path,
              'log_ip':self._remote_addr,
              'user_email':user_email,
              'log_text':errors }
        
        return self._db.add_log_entry(d)
        
    

   
