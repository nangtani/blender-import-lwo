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

import chunk
import struct
import logging
from pprint import pprint
from collections import OrderedDict

from .lwoLogger import LWOLogger


class _lwo_base:
    def __eq__(self, x):
        if not isinstance(x, self.__class__):
            return False
        for k in self.__slots__:
            a = getattr(self, k)
            b = getattr(x, k)
            if not a == b:
                print(f"{k} mismatch:")
                print(f"\t{a} != {b}")
                return False
        return True

    @property
    def dict(self):
        d = OrderedDict()
        for k in self.__slots__:
            d[k] = getattr(self, k)
        return d

    def __repr__(self):
        return str(self.dict)


class _obj_layer(_lwo_base):
    __slots__ = (
        "name",
        "index",
        "parent_index",
        "pivot",
        "pols",
        "bones",
        "bone_names",
        "bone_rolls",
        "pnts",
        "vnorms",
        "lnorms",
        "wmaps",
        "colmaps",
        "uvmaps_vmad",
        "uvmaps_vmap",
        "morphs",
        "edge_weights",
        "surf_tags",
        "has_subds",
    )

    def __init__(self):
        self.name = ""
        self.index = -1
        self.parent_index = -1
        self.pivot = [0, 0, 0]
        self.pols = []
        self.bones = []
        self.bone_names = {}
        self.bone_rolls = {}
        self.pnts = []
        self.vnorms = {}
        self.lnorms = {}
        self.wmaps = {}
        self.colmaps = {}
        self.uvmaps_vmad = {}
        self.uvmaps_vmap = {}
        self.morphs = {}
        self.edge_weights = {}
        self.surf_tags = {}
        self.has_subds = False


class _obj_surf(_lwo_base):
    __slots__ = (
        "name",
        "source_name",
        "colr",
        "diff",
        "lumi",
        "spec",
        "refl",
        "rblr",
        "tran",
        "rind",
        "tblr",
        "trnl",
        "glos",
        "shrp",
        "bump",
        "strs",
        "smooth",
        "textures",
        "textures_5",
    )

    def __init__(self):
        self.name = "Default"
        self.source_name = ""
        self.colr = [1.0, 1.0, 1.0]
        self.diff = 1.0  # Diffuse
        self.lumi = 0.0  # Luminosity
        self.spec = 0.0  # Specular
        self.refl = 0.0  # Reflectivity
        self.rblr = 0.0  # Reflection Bluring
        self.tran = 0.0  # Transparency (the opposite of Blender's Alpha value)
        self.rind = 1.0  # RT Transparency IOR
        self.tblr = 0.0  # Refraction Bluring
        self.trnl = 0.0  # Translucency
        self.glos = 0.4  # Glossiness
        self.shrp = 0.0  # Diffuse Sharpness
        self.bump = 1.0  # Bump
        self.strs = 0.0  # Smooth Threshold
        self.smooth = False  # Surface Smoothing
        self.textures = {}  # Textures list
        self.textures2 = {}  # Textures list
        self.textures_5 = []  # Textures list for LWOB

    def lwoprint(self):  # debug: no cover
        print(f"SURFACE")
        print(f"Surface Name:       {self.name}")
        print(
            f"Color:              {int(self.colr[0]*256)} {int(self.colr[1]*256)} {int(self.colr[2]*256)}"
        )
        print(f"Luminosity:         {self.lumi*100:>8.1f}%")
        print(f"Diffuse:            {self.diff*100:>8.1f}%")
        print(f"Specular:           {self.spec*100:>8.1f}%")
        print(f"Glossiness:         {self.glos*100:>8.1f}%")
        print(f"Reflection:         {self.refl*100:>8.1f}%")
        print(f"Transparency:       {self.tran*100:>8.1f}%")
        print(f"Refraction Index:   {self.rind:>8.1f}")
        print(f"Translucency:       {self.trnl*100:>8.1f}%")
        print(f"Bump:               {self.bump*100:>8.1f}%")
        print(f"Smoothing:          {self.smooth:>8}")
        print(f"Smooth Threshold:   {self.strs*100:>8.1f}%")
        print(f"Reflection Bluring: {self.rblr*100:>8.1f}%")
        print(f"Refraction Bluring: {self.tblr*100:>8.1f}%")
        print(f"Diffuse Sharpness:  {self.shrp*100:>8.1f}%")
        print()
        for textures_type in self.textures.keys():
            print(textures_type)
            for texture in self.textures[textures_type]:
                texture.lwoprint(indent=1)


class _surf_position(_lwo_base):
    __slots__ = (
        "cntr",
        "size",
        "rota",
        "fall",
        "oref",
        "csys",
    )

    def __init__(self):
        self.cntr = (0.0, 0.0, 0.0, 0)
        self.size = (0.0, 0.0, 0.0, 0)
        self.rota = (0.0, 0.0, 0.0, 0)
        self.fall = (0, 0.0, 0.0, 0.0, 0)
        self.oref = ""
        self.csys = 0


class _surf_texture(_lwo_base):
    __slots__ = (
        "opac",
        "opactype",
        "enab",
        "clipid",
        "projection",
        "axis",
        "position",
        "enab",
        "uvname",
        "channel",
        "type",
        "func",
        "image",
        "nega",
    )

    def __init__(self):
        self.clipid = 1
        self.rev = 9
        self.opac = 1.0
        self.opactype = 0
        self.enab = True
        self.projection = 5
        self.axis = 0
        self.position = _surf_position()
        self.uvname = "UVMap"
        self.channel = "COLR"
        self.type = "IMAP"
        self.func = None
        self.image = None
        self.nega = None

    def lwoprint(self, indent=0):  # debug: no cover
        print(f"TEXTURE")
        print(f"ClipID:         {self.clipid}")
        print(f"Opacity:        {self.opac*100:.1f}%")
        print(f"Opacity Type:   {self.opactype}")
        print(f"Enabled:        {self.enab}")
        print(f"Projection:     {self.projection}")
        print(f"Axis:           {self.axis}")
        print(f"UVname:         {self.uvname}")
        print(f"Channel:        {self.channel}")
        print(f"Type:           {self.type}")
        print(f"Function:       {self.func}")
        print(f"Image:          {self.image}")
        print()


class LWOBase:
    def __init__(self, filename=None, loglevel=logging.INFO):
        self.filename = filename
        self.file_types = []
        self.file_type = []
        self.layers = []
        self.surfs = {}
        self.materials = {}
        self.tags = []
        self.clips = {}
        self.images = []
        
        self.pnt_count = 0
        
        self.rootchunk = None
        self.seek = 0

        self.l = LWOLogger("LWO", loglevel)

    @property
    def bytes2(self):
#         self.debug(self.rootchunk)
#         self.debug(self.rootchunk.getsize())
#         self.debug(self.rootchunk.getname())
#         self.debug(self.rootchunk.tell())
        #self.rootchunk.seek(0)
        return self.rootchunk.read()
        
    def debug(self, msg):
         self.l.debug(msg)
        
    def info(self, msg):
        self.l.info(msg)

    def warning(self, msg):
        self.l.warning(msg)

    def error(self, msg):
        if self.l.level < logging.INFO:
            raise Exception(f"{self.filename} {msg}")
        else:
            self.l.error(msg)

    def read_lwostring(self, raw_name):
        """Parse a zero-padded string."""

        i = raw_name.find(b"\0")
        name_len = i + 1
        if name_len % 2 == 1:  # Test for oddness.
            name_len += 1

        if i > 0:
            # Some plugins put non-text strings in the tags chunk.
            name = raw_name[0:i].decode("utf-8", "ignore")
        else:
            name = ""

        return name, name_len

    def read_tags(self):
        """Read the object's Tags chunk."""
        bytes = self.bytes2
        offset = 0
        chunk_len = len(bytes)

        while offset < chunk_len:
            tag, tag_len = self.read_lwostring(bytes[offset:])
            offset += tag_len
            self.tags.append(tag)
        self.seek += offset

    def read_pnts(self):
        """Read the layer's points."""
        bytes = self.bytes2
        self.info(f"    Reading Layer ({self.layers[-1].name }) Points")
        offset = 0
        chunk_len = len(bytes)

        while offset < chunk_len:
            pnts = struct.unpack(">fff", bytes[offset : offset + 12])
            offset += 12
            # Re-order the points so that the mesh has the right pitch,
            # the pivot already has the correct order.
            pnts = [
                pnts[0] - self.layers[-1].pivot[0],
                pnts[2] - self.layers[-1].pivot[1],
                pnts[1] - self.layers[-1].pivot[2],
            ]
            self.pnt_count += 1
            self.layers[-1].pnts.append(pnts)

    def read_lwo(self):
        self.f = open(self.filename, "rb")
        try:
            header, chunk_size, chunk_name = struct.unpack(">4s1L4s", self.f.read(12))
        except:
            self.error(f"Error parsing file header! Filename {self.filename}")
            self.f.close()
            return

        if not chunk_name in self.file_types:
            raise Exception(
                f"Incorrect file type: {chunk_name} not in {self.file_types}"
            )
        self.file_type = chunk_name

        self.info(f"Importing LWO: {self.filename}")
        self.info(f"{self.file_type.decode('ascii')} Format")

        while True:
            try:
                self.rootchunk = chunk.Chunk(self.f)
            except EOFError:
                break
            self.parse_tags()
        del self.f

#         self.chunks = []
#         while True:
#             try:
#                  self.chunks.append(chunk.Chunk(self.f))
#             except EOFError:
#                 break
#         del self.f
#         
#         for rootchunk in self.chunks:
#             self.debug(rootchunk)
#             #self.parse_tags()
#         exit()
