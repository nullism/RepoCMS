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

import Cookie
import re
import urllib
import cgi
import time

##
# A generic web handler
#
class Handler(object):
    
    def __init__(self, environ):
        self._env = environ
        self._headers = {'Content-type':'text/plain',
                         'Cache-Control':'max-age=0, private'}
        self._method = self._env['REQUEST_METHOD']
        self._path = self._env['PATH_INFO']
        self._remote_addr = self._env['REMOTE_ADDR']
        self._user_agent = self._env['HTTP_USER_AGENT']
        self.set_status(200)

        try:
            self._form_data = cgi.FieldStorage(fp=self._env['wsgi.input'],
                                               environ=self._env,
                                               keep_blank_values=1)
        except(Exception),e:
            self._form_data = None

        try:
            self._cookie = Cookie.SimpleCookie(self._env['HTTP_COOKIE'])
        except(Exception),e:
            self._cookie = Cookie.SimpleCookie()

    ##
    # Wrapper for POST and GET 
    # 
    def REQ(self, key, l=False):
        if self._method == 'POST':
            return self.POST(key, l)
        return self.GET(key, l)

    ##
    # Get variables
    #
    def GET(self, key, l=False):
        try:
            return self.urldecode(self._form_data.getvalue(key)).strip()
        except(Exception),e:
            #self._errors.append('%s'%(e))
            return ''

    ##
    # POST variables
    #
    def POST(self, key, l=False):
        try:
            if l: return self._form_data.getlist(key)
            return self.urldecode(self._form_data.getvalue(key)).strip()
        except(Exception),e:
            #self._errors.append('%s'%(e))
            if l: return []
            return ''
    ##
    # FILE (Uploads)
    #
    def FILE(self, key):
        try:
            return self._form_data[key]
        except(Exception),e:
            self._errors.append('%s'%(e))
            return False

    ##
    # COOKIE variables
    #
    def COOKIE(self, key):
        try: 
            return self._cookie[key].value
        except(Exception),e:
            return False


    ##
    # Route the request to the passed function
    #
    def handle_request(self, path_defs):
        for pd in path_defs:
            regex = pd[0]
            methods = pd[1]
            func = pd[2]
            ctype = pd[3]
            p = re.compile(regex, re.UNICODE)
            m = p.search(self._path)
            
            if(m):
                l = m.groups()
        
                if self._method not in methods:
                    self.set_status(405)
                    return False

                if ctype:
                    self.set_header('Content-type',ctype)

                return func(*l)


    ##
    # Generates a header compatible tuples for cookies
    #
    def get_cookie_tuples(self):
        ret = []
        try:
            for l in self._cookie.output().split('\n'):
                i = l.split(': ')
                ret.append((i[0], i[1]))
        except(Exception), e:
            return []
             
        return ret


    ##
    # Generates headers
    # @returns [string] The text based version of the headers dictionary
    #
    def get_headers(self):
        l = []
        for i in self._headers.keys():
            l.append((i,self._headers[i]))
        for t in self.get_cookie_tuples():
            l.append(t)
        return l


    ##
    # Check if mobile device
    # @returns [bool] True if mobile, False otherwise
    #
    def get_is_mobile(self):
        ua = self._user_agent.lower()
        if "android" in ua:
            return True
        elif "iphone" in ua:
            return True
        elif "blackberry" in ua:
            return True

        return False

    ##
    # Return redirect
    #
    def redirect(self, url):
        self.set_status(302)
        self.set_header('Location',url)
        return False

    ##
    # Set a header
    #
    def set_header(self, key, val):
        self._headers[key] = val
        return True

    ##
    # Set the return status
    #
    def set_status(self, code):
        codes = { 
            200:"OK",
            302:"Found",
            400:"Bad Request",
            401:"Unauthorized",
            403:"Forbidden",
            404:"Not Found",
            405:"Method Not Allowed",
        }
        try:
            self._status = "%s %s"%(code, codes[code])
            self._status_code = code
            return True
        except(Exception):
            self._status = "400 Bad Request"
            self._status_code = 400
            return False
       

    ##
    # URL JavaScript compatible encode (with "escape")
    # @param data [string] String to be encoded
    #
    def urlencode(self,data):
        return urllib.quote(data, safe='@-_+./')
    
    
    ##
    # URL JavaScript compatible decoding (with "escape")
    # @param data [string] String to be decoded
    #
    def urldecode(self,data):
        return urllib.unquote(data)  
