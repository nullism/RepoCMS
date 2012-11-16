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

import sys, time, random, os
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"./lib/"))
if path not in sys.path:
    sys.path.insert(0,path)
from dbwrap import DBWrap


class AppDB(DBWrap):  

    ##
    # Add a link
    # @param d [dict] DB Key:Value pairs
    #
    def add_link(self, d):
        sql = '''
              INSERT INTO link 
              (lang_key, 
               link_parent_id, 
               link_path,
               link_name,
               link_title, 
               link_target)
              VALUES 
              (%(lang_key)s,
               %(link_parent_id)s,
               %(link_path)s,
               %(link_name)s,
               %(link_title)s,
               %(link_target)s)
              '''
        return self.sql_execute(sql, d)

       
    ##
    # Add a log entry
    # @param d [dict] DB key:value pairs.
    #
    def add_log_entry(self, d):
        d['log_time'] = d.get('log_time',int(time.time()))
        d['log_type'] = d.get('log_type','generic')
        d['log_path'] = d.get('log_path',None)
        d['log_ip'] = d.get('log_ip',None)
        d['log_text'] = str(d.get('log_text',['No Text']))
        sql = '''INSERT INTO log (log_ip, log_path, 
                                  log_type, log_time, log_text)
                 VALUES (%(log_ip)s, %(log_path)s, 
                         %(log_type)s, %(log_time)s, %(log_text)s)'''
        return self.sql_execute(sql, d)
    
    
    ##
    # Add or update a page entry
    # @param d [dict] DB key:value pairs.
    #
    def add_or_update_page(self, d):
        d['page_modified'] = d.get('page_modified',int(time.time()))
        sql = '''
              INSERT INTO page (page_key, page_title, lang_key, 
                                page_modified, page_text,
                                page_redirect)
              VALUES (%(page_key)s, %(page_title)s, %(lang_key)s, 
                      %(page_modified)s, %(page_text)s,
                      %(page_redirect)s)
              ON DUPLICATE KEY 
                UPDATE page_modified=%(page_modified)s,
                       page_title=%(page_title)s,
                       page_text=%(page_text)s,
                       page_redirect=%(page_redirect)s
              '''
        return self.sql_execute(sql, d)
        
     
    ##
    # Add or update an upload
    # @param d [dict] DB key:value pairs
    #
    def add_or_update_upload(self, d):
        d['upload_modified'] = d.get('upload_modified',
                                     int(time.time()))
        sql = '''
              INSERT INTO upload (upload_basename, upload_modified)
              VALUES (%(upload_basename)s, %(upload_modified)s)
              ON DUPLICATE KEY
                UPDATE upload_modified=%(upload_modified)s
              '''
        return self.sql_execute(sql, d)


    ##
    # Get languages
    #
    def get_languages(self):
        sql = 'SELECT * FROM lang'
        return self.sql_select(sql, False)
        

    ##
    # Get links
    #
    def get_links_by_lang(self, lang_key): 
        sql = '''SELECT * FROM link 
                 WHERE link_parent_id IS NULL
                 AND lang_key=%(lang_key)s'''
        links = self.sql_select(sql, False, {'lang_key':lang_key})
        for l1 in links:
            sql = '''SELECT * FROM link 
                     WHERE link_parent_id=%(link_id)s
                     AND lang_key=%(lang_key)s'''
            links2 = self.sql_select(sql, False, l1)
            l1['link_children'] = links2
            for l2 in links2:
                sql = '''SELECT * FROM link 
                         WHERE link_parent_id=%(link_id)s
                         AND lang_key=%(lang_key)s'''
                links3 = self.sql_select(sql, False, l2)
                l2['link_children'] = links3
        return links


    ##
    # Get page by key
    #
    def get_page_by_key_lang(self, page_key, lang_key):
        sql = '''SELECT * FROM page 
                 WHERE page_key=%(page_key)s 
                 AND lang_key=%(lang_key)s
                 LIMIT 1'''
        return self.sql_select(sql, True, 
                {'page_key': page_key, 'lang_key':lang_key})
        
                
    ##
    # Get page by search
    # 
    def get_pages_by_search(self, search, start=0, limit=25):
        
        sql = '''
              SELECT page_title, page_text, page_key, lang_key,
                     MATCH (page_text) AGAINST (%(search)s IN BOOLEAN MODE) as page_score
              FROM page
              WHERE MATCH (page_text) AGAINST (%(search)s IN BOOLEAN MODE)
              ORDER BY page_score DESC
              LIMIT %(start)s,%(limit)s
              '''
        d = {'search':search+'*', 'start':int(start), 'limit':int(limit)}
        return self.sql_select(sql, False, d)
        
        
    ##
    # Get page by search count
    #
    def get_pages_by_search_total(self, search):
        sql = '''
              SELECT COUNT(*) AS total
              FROM page
              WHERE MATCH (page_text) 
              AGAINST (%(search)s IN BOOLEAN MODE)
              '''
        d = {'search':search+'*'}
        row = self.sql_select(sql, True, d)
        if row:
            return row['total']
        return False

    
    ## 
    # Get upload by basename
    #
    def get_upload_by_basename(self, fname):
        sql = '''SELECT * FROM upload 
                 WHERE upload_basename=%(fname)s
                 LIMIT 1'''
        return self.sql_select(sql, True, {'fname':fname})

        
    ##
    # Remove page
    #
    def remove_page_by_key_lang(self, page_key, lang_key):
        sql = '''DELETE FROM page 
                 WHERE page_key=%(page_key)s
                 AND lang_key=%(lang_key)s LIMIT 1'''
        return self.sql_execute(sql, {'page_key':page_key,
                                      'lang_key':lang_key})
                                      
    ##
    # Remove upload
    #
    def remove_upload_by_mtime(self, mtime):
        sql = '''DELETE FROM upload 
                 WHERE upload_modified < %(mtime)s'''
        return self.sql_execute(sql, {'mtime':mtime})
