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
import re
import sys
import os, shutil
import glob
import imp
import time
import argparse
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../lib/"))
if path not in sys.path:
    sys.path.insert(0,path)
filter_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"/filters/"))
from utility import Utility

class CacheControl(object):
    # Page Buffer
    pb = { 'text':None, 
           'title':None, 
           'keywords':None,
           'description':None,
           'filename':None,
           'filename_cache':None} 
    
    _messages = []
    _errors = []
        
    def __init__(self): 
        self._ut = Utility()
        self._conf = self._ut._conf
        self._db = self._ut._db
        self._jtheme = self._ut._jtheme
        self._jtheme_mobile = self._ut._jtheme_mobile
        self._jcache = self._ut._jcache
     
     
    ##
    # Remove old pages
    #
    def remove_old_pages(self):
        self.out("Removing deleted pages from cache")
        source_pages = []
        # Get current content pages
        for r, d, files in os.walk(self._conf.DIR_CONTENT):
            d[:] = [x for x in d if not x.startswith('.')]
            for f in files:
                fpage = os.path.splitext(os.path.basename(f))[0]
                source_pages.append(fpage)
        
        # Get current cache pages, and remove accordingly.
        for fname in glob.glob(os.path.join(self._conf.DIR_CACHE,'*.html')):
            fpage = os.path.splitext(os.path.basename(fname))[0]
            if fpage not in source_pages:
                ppair = fpage.split('__')
                pkey = ppair[1]
                plang = ppair[0]
                self.out('Removing %s (%s, %s)'%(fpage, plang, pkey))
                self._db.remove_page_by_key_lang(pkey, plang)
                os.remove(fname)
        self.out("Done removing deleted pages from cache")
        
        
    ##
    # Remove old uploads
    #
    def remove_old_uploads(self):
        self.out("Removing uploads not in database...")
        for r, d, files in os.walk(self._conf.DIR_STATIC_UPLOAD):
            d[:] = [x for x in d if not x.startswith('.')]
            for f in files:
                if not self._db.get_upload_by_basename(f):
                    self.out('%s unused, deleting...'%(f))
                    os.remove(os.path.join(r, f))

        self.out("Done removing uploads")
        
        
    ##
    # Run filter
    #
    def run_filter(self, cf, t="pre"):

        text = self.pb['text']

        if self.pb['filetype'] not in cf.filetype_support:
            self.warn('%s not supported by %s: %s'\
                      %(self.pb['filetype'], cf.name, 
                        cf.filetype_support))
            return True
            
        self.out('Start Filter: %s %s...'%(cf.name, cf.version))
        p = re.compile(cf.pattern, re.DOTALL|re.UNICODE)
        cf.debug = []
        matches = p.findall(text)
        for m in matches:
            if type(m) == tuple:
                m = [l for l in m]
            else:
                m = m
            if t.lower() == "pre":
                rep = cf.pre_filter(m)
            else:
                rep = cf.post_filter(m)
            if rep:
                text = re.sub(p, rep, text, 1)
        for msg in cf.debug:
            self.out('>>> %s'%(msg))
        self.pb['text'] = text
        if t == 'pre':
            self.pb['text_with_meta'] = text
        self.out('End Filter: %s %s'%(cf.name, cf.version))
        return True
        
         
    ##
    # Add pre-html filter calls here
    #
    def run_filters(self, t="pre"):
        filtg = os.path.join(self._conf.DIR_BASE, 'filters/*.py')
        self.out("Importing %s-filters in %s"%(t, filtg))
        filter_list = glob.glob(filtg)
        for fpath in sorted(filter_list):
            ( mod_name, file_ext ) = os.path.splitext(os.path.split(fpath)[-1])
            p = re.compile('^[0-9]+\-?')
            filt_name = re.sub(p, '', mod_name)
            if filt_name not in self._conf.ENABLED_FILTERS:
                self.out('Filter %s disabled, skipping'%(mod_name))
                continue
            mod = imp.load_source(mod_name, fpath)
            cf = mod.CustomFilter(self._ut, self.pb)
            self.run_filter(cf, t)
            
            
    ##
    # Cache the links, should be called before "cache menus"
    #
    def cache_links(self, force=False):
        self.out('Caching all links...')
        self._db.sql_execute('DELETE FROM link WHERE link_id IS NOT NULL')
        fnames = glob.glob(os.path.join(self._conf.DIR_CONTENT, '*__links.txt'))
        for fname in fnames:
            self.out('Working on %s...'%(fname))
            mtime = os.stat(fname).st_mtime
            
            if (int(time.time()) - mtime) > 3600 and not force:
                self.out('Links not recently modified, skipping')
                continue
            
            lang = fname.split('/')[-1].split('\\')[-1].split('__')[0]
            fh = open(fname, 'r')
            flines = fh.readlines()
            fh.close()

            link_depth = [None, None, None, None, None]
            
            for line in flines:
                line = line.replace('\n','').strip()
                if line == '' or line.startswith('#'):
                    continue
                parts = [p.strip() for p in line.split('|')]
                if len(parts) < 2:
                    self.out('Invalid link, skipping')
                    continue
                
                if parts[0].startswith('>>>>'):
                    this_depth = 4
                elif parts[0].startswith('>>>'):
                    this_depth = 3
                elif parts[0].startswith('>>'):
                    this_depth = 2
                elif parts[0].startswith('>'):
                    this_depth = 1
                else:
                    this_depth = 0
                
                this_parent_id = None    
                if this_depth:
                    this_parent_id = link_depth[this_depth-1]                
                
                # Parse the link path
                if parts[1].startswith('http://'): 
                    link_path = parts[1]
                elif parts[1].startswith('https://'):
                    link_path = parts[1]
                elif parts[1].startswith('ftp://'):
                    link_path = parts[1]
                elif parts[1].startswith('/'):
                    link_path = parts[1]
                elif parts[1].strip() == '#':
                    link_path = ''
                else:
                    link_path = '%s/%s/%s'%(self._conf.PATH_PREFIX, lang, parts[1])
                    
                # Parse the link title
                if len(parts) > 2:
                    link_title = parts[2]
                else: 
                    link_title = ''
                    
                # Parse the link target
                if len(parts) > 3:
                    link_target = parts[3]
                else:
                    link_target = '_self'

                d = { 'link_name': parts[0].split('>')[-1],
                      'link_title': link_title,
                      'link_path': link_path,
                      'link_parent_id': this_parent_id,
                      'lang_key': lang,
                      'link_target': link_target,
                    }
                self._db.add_link(d)
                if self._db._errors:
                    self.err('Could not add link: %s'%(self._db._errors))
                    continue
                    
                link_depth[this_depth] = self._db._cursor.lastrowid
                
        self.out('Done caching links')
            
    
    ##
    # Cache the menu(s)
    #
    def cache_menus(self):
        self.out('Caching menus')
        langs = self._db.get_languages()
        for lang_d in langs:
            links_d = self._db.get_links_by_lang(lang_d['lang_key'])
            if not links_d:
                continue
                
            tpl = self._jtheme.get_template('menu.html')
            link_html = tpl.render(links=links_d)
            fh = open(os.path.join(self._conf.DIR_CACHE,
                                   'special/%s__menu.html'\
                                   %(lang_d['lang_key'])),'w')
            fh.write(link_html)
            fh.close()
            if self._conf.DIR_THEME != self._conf.DIR_THEME_MOBILE:
                tpl = self._jtheme_mobile.get_template('menu.html')
                link_html = tpl.render(links=links_d)
                fh = open(os.path.join(self._conf.DIR_CACHE,
                                       'special/%s__menu-mobile.html'\
                                       %(lang_d['lang_key'])),'w')
                fh.write(link_html)
                fh.close()

        self.out('Done caching menus')
        
    
    ##
    # Cache page
    #
    def cache_page(self, fname):
        self.pb = {}
        self.load_page_into_buffer(fname)
        self.run_filters("pre")
        self.convert_page()
        self.run_filters("post")
        self.page_to_cache()
        self.page_to_database()
        return True

        
    
    ##
    # Convert the page to the appropriate format
    #
    def convert_page(self):
        
        text = self.strip_meta_filters(self.pb['text'])        
                                
        if self.pb['filename'].endswith('.md'):
            import markdown
            self.out('Converting MarkDown on %s'%(self.pb['filename']))
            text = markdown.markdown(text, output_format='html5')
            
        elif self.pb['filename'].endswith('.rst'):
            from docutils.core import publish_parts
            self.out('Converting to RST on %s'%(self.pb['filename']))
            text = publish_parts(text, writer_name='html')['html_body']
        
        elif self.pb['filename'].endswith('.textile'):
            import textile
            self.out('Converting to Textile on %s'%(self.pb['filename']))
            text = unicode(textile.textile(text))
        
        elif self.pb['filename'].endswith('.txt'):
            self.out('Converting TXT on %s'%(self.pb['filename']))
            text = text.replace('<','&lt;')
            text = text.replace('>','&gt;')
            text = '<pre>%s</pre>'%(text)
            
        else:
            self.out('Treating as html')
            self.pb['filetype'] = 'html'
        
        self.pb['text'] = text
        self.out('Done with conversion')
        return True
        
    ##
    # Filter out the non-jinja filters
    #
    def get_meta_data(self, key):
         
        regex = r'\(\((\s{0,1}%s.*?)\)\)'%(key)            
        p = re.compile(regex)
        m = p.search(self.pb['text_with_meta'])
        if m:
            data = m.groups()[0]
            data = [d.strip() for d in data.split('|')]
            return data[1:]
        return []

    ##
    # Get the date / time stamp
    #
    def get_date(self):
        d = self.get_meta_data('date')
        if d:
            epoch = int(time.mktime(
                time.strptime(d[0],self._conf.TIME_STRING)
                ))
            print "EPOCH IS: %s"%(epoch)
            return epoch
        return int(time.time())

    ##
    # Get the description
    #    
    def get_description(self):
        d = self.get_meta_data('description')
        if d: 
            return d[0]
        return None
        
        
    ##
    # Get the keywords
    #    
    def get_keywords(self):
        k = self.get_meta_data('keywords')
        if k:
            return [w.strip().lower() for w in k[0].split(',')]
        return []
        
    
    ##
    # Get the redirect data
    #
    def get_redirect(self):
        r = self.get_meta_data('redirect')
        if r:
            lang = self.get_page_lang()
            if r[0].startswith('/%s'%(lang)):
                return r[0]
            elif r[0].startswith('http:') or r[0].startswith('https:'):
                return r[0]
            else:
                return '/%s/%s'%(lang, r[0])
        return None
        
    
    ##
    # Get the minified text
    # 
    def get_text_min(self):
        tmin = self.pb['text']
        html_re = r'(\<.*?\>)'
        p = re.compile(html_re)
        tmin = re.sub(p,'',tmin)
        
        filt1_re = r'(\(\(.*?\)\))'
        p = re.compile(filt1_re)
        tmin = re.sub(p,'',tmin)
        
        filt2_re = r'(\[\[.*?\]\])'
        p = re.compile(filt2_re)
        tmin = re.sub(p,'',tmin)
        
        filt3_re = r'(\{\{.*?\}\})'
        p = re.compile(filt3_re)
        tmin = re.sub(p,'',tmin)
        
        filt4_re = r'(\{\%.*?\%\})'
        p = re.compile(filt4_re)
        tmin = re.sub(p,'',tmin)
        
        tmin = tmin.replace('\n',' ')
        tmin.strip()
        return tmin

    
    ##
    # Get the title
    #    
    def get_title(self):
        t = self.get_meta_data('title')
        if t:
            return t[0]
        title = self.pb['filename'].split('/')[-1]\
                .split('\\')[-1].split('__')[-1].split('.')[0]
        return title

        
    ##
    # Get page key
    #
    def get_page_key(self): 
        pkey = os.path.basename(self.pb['filename'])
        pkey = pkey.split('.')[0].split('__')[-1]
        return pkey

            
    ##
    # Get page filename cache
    #
    def get_page_filename_cache(self):
        # Load page into buffer
        fname = self.pb['filename']
        fname_cache = fname.split('/')[-1].split('\\')[-1]
        fname_cache = fname_cache.replace('.'+fname_cache.split('.')[-1],'.html')
        fname_cache = os.path.join(self._conf.DIR_CACHE, fname_cache)
        return fname_cache

        
    ##
    # Get page language
    #
    def get_page_lang(self):
        lang = self.pb['filename']
        lang = os.path.basename(lang).split('__')[0]
        return lang

    
    ##
    # do_page_caching
    #
    def do_page_caching(self, force=False):
        
        source_dir = self._conf.DIR_CONTENT
        self.out('Caching pages in %s'%(source_dir))    
        for r, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            dirs[:] = [d for d in dirs if d != self._conf.DIR_UPLOAD_NAME]
            for f in files:
                fname = os.path.join(r, f)
                mtime = os.stat(fname).st_mtime
                lang = f.split('__')[0]
                key = f.split('__')[-1].split('.')[0]
                dbpage = self._db.get_page_by_key_lang(key, lang)
                
                # Basic checks
                if not force and dbpage:
                    if dbpage['page_modified'] >= mtime:
                        self.out('Not recently modified: %s, skipping'%(f))
                        continue
                if f.startswith('.'):
                    self.out('%s hidden, skipping'%(f))
                    continue
                if '__' not in f:
                    self.err('Could not get language of %s'%(f))
                    continue
                if f.split('.')[-1] not in ['txt','md','html','rst','textile']:
                    self.err('Could not determine type of %s'%(f))
                    continue 
                if len(lang) != 3:
                    self.err('Could not determine language of %s'%(f))
                    continue
            
                try:
                    self.cache_page(fname)
                except(Exception),e:
                    self.err('%s - %s'%(fname, e))
                    
        self.remove_old_pages()

                    
    ##
    # Do upload caching
    #
    def do_upload_caching(self, force=False):
        source_dir = self._conf.DIR_CONTENT_UPLOAD
        self.out('Caching uploads in %s'%(source_dir))    
        for r, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for f in files:
                fname = os.path.join(r, f)
                mtime = os.stat(fname).st_mtime
                upload_d = self._db.get_upload_by_basename(f)
                
                # Add or update modified time to database
                d = {'upload_basename':f}
                self._db.add_or_update_upload(d)
                
                if not force and upload_d:
                    if upload_d['upload_modified'] >= mtime:
                        self.out('Not recently modified, skipping')
                        continue
                        
                # Copy into target directory
                shutil.copy2(fname, self._conf.DIR_STATIC_UPLOAD)
                
        self.out('Done caching uploads')
                
                
    ##
    # Load page into buffer
    #
    def load_page_into_buffer(self, fname):
        self.out('Loading %s into buffer'%(fname))
        self.pb['text_with_meta'] = unicode(open(fname, 'r').read().decode('utf-8'))
        self.pb['text'] = self.pb['text_with_meta']
        self.pb['filename'] = fname   
        self.pb['filetype'] = fname.split('.')[-1]     
        self.pb['filename_cache'] = self.get_page_filename_cache()
        self.pb['key'] = self.get_page_key()
        self.pb['lang'] = self.get_page_lang()
        self.out('Done loading page')
    
 
    ## 
    # Purge uploads no longer in use
    #
    def purge_uploads(self):
        self.out("Purging deleted or unused uploads...")
        time_start = int(time.time())
        self.do_page_caching(True)
        self.do_upload_caching(True)
        self._db.remove_upload_by_mtime(time_start)
        self.remove_old_uploads()
        total_time = int(time.time()) - time_start
        self.out("Done purging uploads, %s seconds"%(total_time))
     
    
    ##
    # Add page to cache
    #
    def page_to_cache(self):
        self.out('Caching to %s'%(self.pb['filename_cache']))
        fh = open(self.pb['filename_cache'], 'w')
        fh.write(self.strip_meta_filters(self.pb['text'].encode('utf-8')))
        fh.close()
        self.out('Done caching')
        
        
    ##
    # Add page to database
    #
    def page_to_database(self):
        self.out('Updating database for %s'%(self.pb['key']))
        page_d = { 
                  'page_text': self.get_text_min().encode('utf-8'),
                  'page_key': self.pb['key'],
                  'page_title': self.get_title(),
                  'page_keywords': self.get_keywords(),
                  'page_description': self.get_description(),
                  'page_created': self.get_date(),
                  'page_redirect': self.get_redirect(),
                  'lang_key': self.pb['lang'],
                 }
        self._db.add_or_update_page(page_d)
        if self._db._errors:
            self.err('Problem adding page: %s'%(self._db._errors))
        self.out('Done updating database')
    
 
    ##
    # Strip meta filters
    #
    def strip_meta_filters(self, text):
        filt_re = r'(\(\(.*?\|.*?\)\))'
        p = re.compile(filt_re)
        return re.sub(p,'',text)
        
    
    ##
    # Output
    #
    def out(self, strn):
        self._messages.append(strn)
        if not self.silent:
            print "OKAY: %s"%(strn)
            

    ##
    # Errors
    #
    def err(self, strn):
        self._errors.append(strn)
        if not self.silent:
            print "ERROR: %s"%(strn)
            

    ##
    # Warning
    #
    def warn(self, strn):
        self._messages.append(strn)
        if not self.silent:
            print "WARNING: %s"%(strn)        
            
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RepoCMS Filter Utilities')
    cc = CacheControl()
    cc.silent = False
    
    parser.add_argument('--cache-pages', dest='cache_pages',
                        action='store_true',
                        help='Cache all pages to the cache dir')
                    
    parser.add_argument('--cache-page', dest='cache_page', 
                        help='Cache a specific page')
                    
    parser.add_argument('--cache-menus', dest='cache_menus',
                    action='store_true',
                    help='Cache all menus to the cache dir')
    
    parser.add_argument('--cache-uploads', dest='cache_uploads',
                    action='store_true',
                    help='Cache all uploads to the static upload dir')
                    
    parser.add_argument('--cache-force', dest='cache_force',
                    action='store_true',
                    help='Force the recache')
                    
    parser.add_argument('--purge-uploads', dest='purge_uploads',
                    action='store_true',
                    help='Delete any unused or deleted uploads - intensive')
                    
    args = parser.parse_args()
    
    if args.cache_uploads:
        cc.do_upload_caching(args.cache_force)
    if args.cache_pages:
        cc.do_page_caching(args.cache_force)
    if args.cache_page:
        cc.cache_page(args.cache_page)
    if args.cache_menus:
        cc.cache_links(args.cache_force)
        cc.cache_menus()
    if args.purge_uploads:
        cc.purge_uploads()

        
