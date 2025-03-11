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
import bpy
import mathutils
from collections import OrderedDict
from pprint import pprint
from .bpy_debug import DebugException

class _material:
    __slots__ = (
        "name",
        "mat",
        "smooth",
    )

    def __init__(self, name=None):
        self.name = name
        self.mat = None
        self.smooth = False


def get_existing(surf, use_existing_materials):
    m = None
    if not use_existing_materials:
        return m
    x = bpy.data.materials.get(surf.name)
    if x is None:
        m = _material(surf.name)
        m.mat = x
        m.smooth = surf.smooth
    return m


def lwo2cycles(surf_data):
    m = _material(surf_data.name)
    mat_name = surf_data.name

    m.smooth = surf_data.smooth
    m.mat = bpy.data.materials.new(mat_name)
    m.mat.use_nodes = True
    nodes = m.mat.node_tree.nodes
    #n = nodes["Material Output"]

        if (2, 80, 0) < bpy.app.version:
            pass
        else:  # else bpy.app.version
            self.m.mat.diffuse_color = self.surf_data.colr[:]
            self.d = nodes.new("ShaderNodeBsdfPrincipled")
            self.m.mat.node_tree.links.new(self.d.outputs["BSDF"], self.n.inputs["Surface"])
            self.nodes.remove(self.nodes["Diffuse BSDF"])
        # endif
            
        self.d = self.nodes["Principled BSDF"]
        self.d.inputs[0].default_value = self.color   
        self.d.location = (self.dx, self.dy)

    for textures_type, textures in surf_data.textures.items():
        for texture in textures:
            if self.textures_type == "COLR":
                self.d_index = "Base Color"
            elif self.textures_type == "SPEC":
                self.d_index = "Specular"
            else:
                self.d_index = None

#                 if textures_type == "COLR":
#                     bsdf_input = d.inputs["Base Color"]
#                 elif textures_type == "SPEC":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "LUMI":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "DIFF":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "REFL":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "TRAN":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "TRNL":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "RIND":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "BUMP":
#                     bsdf_input = d.inputs["Specular"]
#                 elif textures_type == "GLOS":
#                     bsdf_input = d.inputs["Specular"]
#                 else:
#                     continue
            self.v_offset -= 600
            t_offset -= 600
            f.height = f.height - t_offset
            
            self.layer(texture, fx, fy)
#         #f.shrink = True
        if None == self.node_output or None == self.d_index:
            pass
            if self.textures_type == "COLR": 
                pass
                #raise DebugException(f"{self.node_output} {self.d_index} {self.textures_type}")
        else:
            self.m.mat.node_tree.links.new(self.node_output, self.d.inputs[self.d_index])
    
    def layer(self, texture, dx, dy, t_offset=0):
        if "IMAP" == texture.type:
            
            image_path = texture.image
            if image_path is None:
                continue

            basename = os.path.basename(image_path)
            image = bpy.data.images.get(basename)
            if image is None:
                image = bpy.data.images.load(image_path)
            i.image = image
            # print(ci, image)

    return m
