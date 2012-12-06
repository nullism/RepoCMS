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
import MySQLdb

class DBWrap(object):

    def __init__(self, host, user, passwd, db):
        
        self.db = MySQLdb.connect(host,
                                  user,
                                  passwd,
                                  db, use_unicode=True, charset='utf8')
        self._cursor = self.db.cursor()
        self._errors = []
        self._debug = []


    ##
    # A shitty hack for dealing with Python's inability to return DB Dicts. 
    # @param data [object] A mysql single row object from cursor.fetchall()
    # @returns [dict] A dictionary of row columns and values for a single row
    #
    def sql_row2assoc(self,data):
        
        if data == None :
            return None
        desc = self._cursor.description
        rows = {}
        for (name, value) in zip(desc, data) :
            if isinstance(value, basestring):
                if not isinstance(value, unicode):
                    value = unicode(value.decode('utf-8'))
            rows[name[0]] = value
        return rows
    
    
    ##
    # Execute a SELECT statement, returns a list of dictionary rows.
    # @param sql [String] The SELECT statement to execute
    # @returns [list] Like [{'id':123,'name':'Phil McKraken'},{'id'...}] 
    #
    def sql_select(self,sql, single=False, d=None):
        try:
            if(d):
                self._cursor.execute(sql,d)
            else:
                self._cursor.execute(sql)
                
            rows = self._cursor.fetchall()
        except(Exception),e:
            self._errors.append('SEL ERR: %s (%s)'%(e,sql))
            return False
        if not rows: 
            if single:
                return {}
            return []
        l = []
        for row in rows:
            l.append(self.sql_row2assoc(row))
        if single:
            return l[0]
        return l
        
    ##
    # Execute any SQL statement, return the result
    #
    def sql_execute(self, sql, d=None):
        try:
            if d:
                res = self._cursor.execute(sql,d)
            else:
                res = self._cursor.execute(sql)
            self.db.commit()
            return True
        except(Exception),e:
            if d: 
                sql = sql%(d)
            self._errors.append('EXE ERR: %s (%s)'%(e, sql))
            return False



