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
import cherrypy
import sys
import traceback
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
if path not in sys.path:
    sys.path.insert(0,path)
import conf
import pathdefs


def application(environ, start_response):
    (page, paths) = pathdefs.get_paths(environ)
    try:
        output = page.handle_request(paths)
        if not output:
            #output = "Nothing to do (%s) %s"%(page._method, page._status)
            if page._status_code == 302:
                output = ''
            else:
                page.set_header('Content-type','text/html')
                output = page.template_404()
            
    except(Exception) as e: 
        page.set_header('Content-type','text/plain')
        output = 'Error: %s\nTB: %s'%(e, traceback.format_exc())
    
    start_response(page._status, page.get_headers())
    return [output.encode('utf-8')]

if __name__ == "__main__":
    try: 
        port = int(sys.argv[1])
    except:
        print "Usage: %s <port>"%(sys.argv[0])
        sys.exit(1)
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = port
    cherrypy.tree.graft(application, conf.PATH_PREFIX + '/')
    cherrypy.tree.mount(None, conf.PATH_STATIC, {'/' : {
        'tools.staticdir.dir': conf.DIR_STATIC,
        'tools.staticdir.on': True,
        }})
    cherrypy.engine.start()
    cherrypy.engine.block()
