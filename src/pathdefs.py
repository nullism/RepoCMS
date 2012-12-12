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

from page import Page

def get_paths(environ):
    page = Page(environ)
    paths = (   
            (r'^/{0,1}$', ['GET','POST'], page.html_index, "text/html"),
            (r'^/(\w\w\w)/{0,1}$', ['GET','POST'], page.html_index, "text/html"),
            (r'^/(\w\w\w)/pages/by(\w+)/([\w\s]+)/{0,1}$', ['GET','POST'], page.html_page_list, "text/html"),
            (r'^/(\w\w\w)/pages/by(\w+)/(\w+)/(\d+)/(\d+)/{0,1}$', ['GET','POST'], page.html_page_list, "text/html"),
            (r'^/(\w\w\w)/pages/by(\w+)/{0,1}$', ['GET','POST'], page.html_page_list, "text/html"), 
            (r'^/(\w\w\w)/search/{0,1}$', ['GET','POST'], page.html_search, "text/html"),
            (r'^/(\w\w\w)/search/(\d+)/(\d+)/{0,1}$', ['GET','POST'], page.html_search, "text/html"),
            (r'^/(\w\w\w)/([0-9a-zA-Z\-\_]+)/{0,1}$', ['GET','POST'], page.html_page, "text/html"),
            )
    return page, paths
