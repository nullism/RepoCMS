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

import sys
import conf
import argparse

class Setup(object):

    
    def __init__(self):

        self._messages = []
        self._errors = []


        self.out("Trying to load configuration... ",0)
        self._conf = conf
        self.out("[OKAY]")

        self.out("Trying to connect to database... ",0)
        from appdb import AppDB
        self._db = AppDB(self._conf.DB_HOST,
                         self._conf.DB_USER,
                         self._conf.DB_PASS,
                         self._conf.DB_BASE)  
        self.out("[OKAY]") 


    def requirement_check(self):

        self.out("START: Checking for python modules")        

        self.out("Checking for python-mysqldb... ", 0)
        import MySQLdb
        self.out("[OKAY]")

        self.out("Checking for python-jinja2... ",0)
        import jinja2
        self.out("[OKAY]")

        self.out("Checking for python-markdown <optional>... ", 0)
        try:
            import markdown
            self.out("[OKAY]")
        except(Exception),e:
            self.out("[FAILED]")            

        self.out("Checking for python-docutils <optional>... ", 0)
        try:
            import docutils
            self.out("[OKAY]")
        except(Exception),e:
            self.out("[FAILED]")

        self.out("Checking for python-lxml <optional>... ", 0)
        try:
            import lxml.html
            self.out("[OKAY]")
        except(Exception),e:
            self.out("[FAILED]")

        self.out("Checking for python-imaging <optional>... ", 0)
        try:
            import PIL
            self.out("[OKAY]")
        except(Exception),e:
            self.out("[FAILED]")
   
        self.out("Checking for python-textile <optional>... ", 0)
        try:
            import textile
            self.out("[OKAY]")
        except(Exception),e:
            self.out("[FAILED]")

        self.out("END: Checking for python modules")
 

    def create_tables(self):
        self.out("START: Creating tables")
        self.out("Trying to load setup.sql...")
        try:
            fh = open('setup.sql', 'r')
            self.out("[DONE]")
        except(Exception),e:
            self.err("[FAILED]")

        lines = fh.readlines()
        for line in lines:
            line = line.replace('\n','')
            if line.strip() == '':
                continue
            self.out("Running: %s"%(line))

        self.out("END: Creating tables")
            

    def out(self, strn, nl=1):
        self._messages.append(strn)
        sys.stdout.write('%s'%(strn))
        if nl:
            sys.stdout.write('\n')
        sys.stdout.flush()


    def err(self, strn):
        self._errors.append(strn)
        print 'ERROR: %s'%(strn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup the database')

    parser.add_argument('--create-tables', dest='create_tables',
                        action='store_true', 
                        help='Create database tables')
    
    parser.add_argument('--check-requirements', dest='check_requirements',
                        action='store_true', 
                        help='Check requirements')

    args = parser.parse_args()  
    setup = Setup()

    if args.check_requirements:
        setup.requirement_check()
    if args.create_tables:
        setup.create_tables()
    
