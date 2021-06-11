# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import re
import logging
from glob import glob
from pprint import pprint
from collections import OrderedDict

from .lwoDetect import LWODetect
from .lwoLogger import LWOLogger
from .lwoExceptions import lwoNoImageFoundException

class chd:
    def __init__(self):
        self.load_hidden = True
        self.skel_to_arm = False
        self.search_paths = []
        self.recursive = True
        self.images = {}
        self.cancel_search = False

class lwoObject:
    
    def __init__(self, filename, loglevel=logging.INFO):
        self.name, self.ext = os.path.splitext(os.path.basename(filename))
        self.filename = os.path.abspath(filename)
        self.dirpath = os.path.dirname(self.filename)

        self.allow_images_missing = False
        self.absfilepath = True
        self.cwd = os.getcwd()
        self.loglevel = loglevel
        
        self.l = LWOLogger("WRAP", self.loglevel)
        self.ch = chd()
        
    @property
    def layers(self):
        return self.lwo.layers
        
    @property
    def surfs(self):
        return self.lwo.surfs
        
    @property
    def materials(self):
        return self.lwo.materials
        
    @property
    def tags(self):
        return self.lwo.tags

    @property
    def clips(self):
        return self.lwo.clips

    @property
    def images(self):
        return self.lwo.images
        
        
    def __eq__(self, x):
        __slots__ = (
            "layers",
            "surfs",
            "tags",
            "clips",
            "images",
        )
        for k in __slots__:
            a = getattr(self, k)
            b = getattr(x, k)
            if not a == b:
                #                 print(f"{k} mismatch:")
                #                 print(f"\t{a} != {b}")
                return False
        return True

    def read(self, ch=None):
        if not ch is None:
            self.ch = ch

        self.lwo = LWODetect(self.filename, self.loglevel)
        self.lwo.ch = self.ch
        self.lwo.read_lwo()
        

    @property
    def elements(self):
        layers = []
        for x in self.layers:
            layers.append(x.dict)
        surfs = {}
        for x in self.surfs:
            surfs[x] = self.surfs[x].dict
        d = OrderedDict()
        d["layers"] = layers
        d["surfs"] = surfs
        d["tags"] = self.tags
        d["clips"] = self.clips
        d["images"] = self.images
        return d
    
    def pprint(self):
        pprint(self.elements)

    @property
    def search_paths(self):
        paths = [self.dirpath]
        for s in self.ch.search_paths:
            if not re.search("^/", s) and not re.search("^.:", s):
                x = os.path.join(self.dirpath, s)
                y = os.path.abspath(x)
                paths.append(y)
            else:
                paths.append(s)
        return paths
    
    def resolve_clips(self):
        files = []
        for search_path in self.search_paths:
            files.extend(glob(f"{search_path}/**/*.*", recursive=self.ch.recursive))
        
        for c_id in self.clips:
            clip = self.clips[c_id]
            # LW is windows tools, so windows path need to be replaced
            # under linux, and treated the sameunder windows
            imagefile = os.path.basename(clip.replace('\\', os.sep))
            ifile = None
            for f in files:
                if re.search(re.escape(imagefile), f, re.I):
                    if self.absfilepath:
                        ifile = os.path.abspath(f)
                    else:
                        ifile = os.path.relpath(f)

                    if ifile not in self.images:
                        self.images.append(ifile)
                    continue
            
            self.ch.images[c_id] = ifile

        for c_id in self.clips:
            if None is self.ch.images[c_id] and not self.ch.cancel_search:
                raise lwoNoImageFoundException(
                    f"Can't find filepath for image: \"{self.clips[c_id]}\""
                )

    def validate_lwo(self):
        self.l.info(f"Validating LWO: {self.filename}")
        self.l.info(f"{self.lwo.pnt_count} points")
        for surf_key in self.surfs:
            surf_data = self.surfs[surf_key]
            for textures_type in surf_data.textures.keys():
                for texture in surf_data.textures[textures_type]:
                    ci = texture.clipid
                    if ci not in self.clips.keys():
                    #if ci not in self.ch.images.keys():
                        self.l.debug(f"WARNING in material {surf_data.name}")
                        self.l.debug(f"    ci={ci}, not present in self.clips.keys():")
                        self.ch.images[ci] = None
                    texture.image = self.ch.images[ci]

#             for texture in surf_data.textures_5:
#                 ci = texture.id
#                 texture.image = self.ch.images[ci]
            
            for textures_type in surf_data.textures2.keys():
                for texture in surf_data.textures2[textures_type]:
                    ci = texture.clipid
                    self.l.debug(f"{ci}")

