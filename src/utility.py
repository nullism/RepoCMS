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

import sys, os
import time
import subprocess
import argparse
import imp
from hashlib import sha1
from jinja2 import Environment, FileSystemLoader
import custom_jinja_filters
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"./lib/"))
if path not in sys.path:
    sys.path.insert(0,path)

import conf 
from appdb import AppDB

class Utility(object):
    

    def __init__(self):
        self._conf = conf
        self._db = AppDB(self._conf.DB_HOST, 
                         self._conf.DB_USER, 
                         self._conf.DB_PASS, 
                         self._conf.DB_BASE)
        self._template_add = {}
        self._errors = []
        self._messages = []
        self._jtheme = Environment(loader=FileSystemLoader([self._conf.DIR_THEME, self._conf.DIR_THEME_DEFAULT]))
        self._jtheme_mobile = self._jtheme
        if self._conf.DIR_THEME != self._conf.DIR_THEME_MOBILE:
            self._jtheme_mobile = Environment(loader=FileSystemLoader([self._conf.DIR_THEME_MOBILE, self._conf.DIR_THEME_DEFAULT]))
        theme_mod = imp.load_source('theme',os.path.join(self._conf.DIR_THEME, 'theme.py'))
        self._theme_data = theme_mod.theme_data
        self._jcache = Environment(loader=FileSystemLoader(self._conf.DIR_CACHE))
        self.silent = True

        # Define custom filters
        self._jtheme.filters['timedelta'] = custom_jinja_filters.timedelta
        self._jtheme_mobile.filters['timedelta'] = custom_jinja_filters.timedelta
        self._jtheme.filters['timestamp'] = custom_jinja_filters.timestamp
        self._jtheme_mobile.filters['timestamp'] = custom_jinja_filters.timestamp        
        
    ##
    # Wrapper: Translate
    # 
    def _(self, strn):
        return strn
            
        
    ##
    # Sendmail wrapper
    #
    def email_send(self, t, f, s, body, reply_to=None):
        if not f:
            f = self._conf.EMAIL_NOREPLY
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body,'html')
        msg['To'] = t
        msg['From'] = f
        msg['Subject'] = s
        if reply_to: 
            msg.add_header('reply-to',reply_to)
        sm = smtplib.SMTP('localhost')
        sm.sendmail(f, [t], msg.as_string())
        sm.quit()
        return True     


    ##
    # Make password hash
    # 
    def make_password_hash(self, pword):
        return sha1('%s%s'%(pword,self._conf.PW_SALT)).hexdigest()     
        
               
    ##
    # Render a simple template
    #
    def template(self, f, add=None):
        return self._jtheme.get_template(f).render(add=add)
        
    
if __name__ == "__main__":
    pass
        
      
