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
import os
import time
from PIL import Image, ImageOps

class CustomFilter(object):
    
    name = 'image'
    description = 'Parses thumbnails from images'
    author = 'Aaron Meier'
    version = '1.0'
    usage = '[[image|base_filename.png|<width>|<height>|<scaletype>|<cssclass>]]'
    pattern = '\[\[\s?image\|(.*?)\]\]'
    thumbnail_target = '_blank'
    filetype_support = ['html', 'md', 'rst','textile']
    debug = []
    
    def __init__(self, ut, pb):
        self._ut = ut
        self._conf = ut._conf
        self._db = ut._db
        self.pb = pb
     
    ##
    # Parse image thumbnails
    # @param fname [str] Basename of the image file
    # @param w [int] Thumbnail pixel width
    # @param h [int] Thumbnail pixel height
    # @param scale_type [str] Thumbnail type, either 'fit' or 'thumb'
    #        
    def make_thumbnail(self, fname, w=640, h=480, scale_type='thumb'):
            fname = os.path.basename(fname)
            try:
                im = Image.open(os.path.join(
                                self._conf.DIR_CONTENT_UPLOAD, fname))
            except(Exception),e:
                self.debug.append('ERROR: Invalid image file %s - %s'%(fname, e))
                return False
            
            if scale_type == 'thumb':
                im.thumbnail((w,h), Image.ANTIALIAS)
            else:
                im = ImageOps.fit(im, (w, h), Image.ANTIALIAS, (0.5, 0.5))
            fbasename = os.path.basename(fname)
            thumbfname = os.path.join(self._conf.DIR_STATIC_UPLOAD, 
                                      "thumb_%sx%s_%s"%(w,h,fbasename))
            im.save(thumbfname, "PNG", quality=100)
            return thumbfname

    ##
    # Make thumbnails from images
    # @usage [[image|filename.png|w|h]]
    #
    def pre_filter(self, match):
        
        self.debug.append('Found image match: %s'%(match))
        mlist = [i.strip() for i in match.split('|')]
        image = mlist[0]
        width = None
        height = None
        scale_type = 'thumb'
        css_class = 'thumbnail'
        if(len(mlist) > 1) and mlist[1]: 
            width = int(mlist[1])
        if(len(mlist) > 2) and mlist[2]:
            height = int(mlist[2])
        if(len(mlist) > 3) and mlist[3]:
            if scale_type in ['thumb','fit']:
                scale_type = mlist[3]
        if(len(mlist) > 4) and mlist[4]:
            css_class = '%s %s'%(css_class, mlist[4])
       
        if width and height: 
            fname_thumb = self.make_thumbnail(image, width, height, scale_type)
        else: 
            fname_thumb = self.make_thumbnail(image)
            
        if not fname_thumb:
            self.debug.append('Unable to make thumbnail: %s'\
                              %(self._ut._errors))
            return False
            
        path_thumb = self._conf.PATH_UPLOAD\
                   + '/%s'%(os.path.basename(fname_thumb))
        path_image = self._conf.PATH_UPLOAD\
                   + '/%s'%(os.path.basename(image))
            
        result = '<p class="%s"><a href="%s" target="%s"><img src="%s"/></a></p>'\
                 %(css_class, path_image, self.thumbnail_target, path_thumb)
        
        if self.pb['filetype'] == 'rst':
            result = '\n.. raw:: html\n\n    %s\n'%(result)
        elif self.pb['filetype'] == 'textile':
            result = '\nnotextile.. %s\n'%(result)
                 
        d = {'upload_basename':os.path.basename(fname_thumb), 
             'upload_modified':int(time.time())}
        res = self._db.add_or_update_upload(d)
        if self._db._errors:
            self.debug.append('Unable to add upload: %s'\
                              %(self._db._errors))
        
        return result
        
    def post_filter(self, match):
        return match
