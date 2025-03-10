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
    if not None == x:
        m = _material(surf.name)
        m.mat = x
        m.smooth = surf.smooth
    return m


def lwo2BI(surf_data):
    if (2, 80, 0) < bpy.app.version:
        # return # FIXME
        raise Exception("Blender Internal has been removed")
    # endif
    m = _material(surf_data.name)
    m.smooth = surf_data.smooth
    m.mat = bpy.data.materials.new(surf_data.name)
    m.mat.diffuse_color = surf_data.colr[:]
    m.mat.diffuse_intensity = surf_data.diff
    m.mat.emit = surf_data.lumi
    m.mat.specular_intensity = surf_data.spec
    if 0.0 != surf_data.refl:
        m.mat.raytrace_mirror.use = True
    m.mat.raytrace_mirror.reflect_factor = surf_data.refl
    m.mat.raytrace_mirror.gloss_factor = 1.0 - surf_data.rblr
    if 0.0 != surf_data.tran:
        m.mat.use_transparency = True
        m.mat.transparency_method = "RAYTRACE"
    m.mat.alpha = 1.0 - surf_data.tran
    m.mat.raytrace_transparency.ior = surf_data.rind
    m.mat.raytrace_transparency.gloss_factor = 1.0 - surf_data.tblr
    m.mat.translucency = surf_data.trnl
    m.mat.specular_hardness = (
        int(4 * ((10 * surf_data.glos) * (10 * surf_data.glos))) + 4
    )

    for textures_type, textures in surf_data.textures.items():
        for texture in textures:
            if not textures_type == "COLR":
                continue
            tex_slot = m.mat.texture_slots.add()
            image_path = texture.image
            if None == image_path:
                continue

            # print(image_path)
            basename = os.path.basename(image_path)
            image = bpy.data.images.get(basename)
            if None == image:
                image = bpy.data.images.load(image_path)

            tex = bpy.data.textures.new(basename, "IMAGE")
            tex.image = image
            tex_slot.texture = tex
            if texture.projection == 5:
                tex_slot.texture_coords = "UV"
                tex_slot.uv_layer = texture.uvname
            tex_slot.diffuse_color_factor = texture.opac
            # if not (texture.enab):
            #    tex_slot.use_textures[ci - 1] = False

    for texture in surf_data.textures_5:
        tex_slot = m.mat.texture_slots.add()
        if not None == texture.image:
            tex = bpy.data.textures.new(os.path.basename(texture.image), "IMAGE")
            if not (bpy.data.images.get(texture.image)):
                image = bpy.data.images.load(texture.image)
            tex.image = image
            tex_slot.texture = tex
        tex_slot.texture_coords = "GLOBAL"
        tex_slot.mapping = "FLAT"
        if texture.X:
            tex_slot.mapping_x = "X"
        if texture.Y:
            tex_slot.mapping_y = "Y"
        if texture.Z:
            tex_slot.mapping_z = "Z"

    return m

class cymat:
    
    def __init__(self, surf_data):
        self.surf_data = surf_data
        self.mat_name = self.surf_data.name
        self.dx, self.dy = (-300.0, 300.0)
        
        self.m = _material(self.surf_data.name)
        self.m.smooth = self.surf_data.smooth
        
        self.m.mat = bpy.data.materials.new(self.mat_name)
        self.m.mat.use_nodes = True
        self.nodes = self.m.mat.node_tree.nodes
        
        self.surf_data.lwoprint()
        self.color = (self.surf_data.colr[0], self.surf_data.colr[1], self.surf_data.colr[2], self.surf_data.diff)

        self.texture_list = OrderedDict({
            "COLR": [],
            "SPEC": [],
            "DIFF": [],
            "REFL": [],
            "TRAN": [],
            "TRNL": [],
            "RIND": [],
            "BUMP": [],
            "GLOS": [],
            "LUMI": [],
        })
        self.node_output = None
        self.d_index = None

        self.setup_output()
        self.collect_textures()
        
    
    def setup_output(self):
        self.n = self.nodes["Material Output"]
        self.n.location = (self.dx+300, self.dy)

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

    def collect_textures(self):
        
        for textures_type, textures in self.surf_data.textures.items():
            if not textures_type in self.texture_list.keys():
                raise DebugException(f"Unknown Texture Type {textures_type}")
            self.texture_list[textures_type].extend(textures)

        self.v_offset = 0
        for self.textures_type, textures in self.texture_list.items():
            self.build_textures(textures)
    
    def build_textures(self, textures):
        if 0 == len(textures):
            return
        
        fx = self.dx-920.0
        fy = self.dy+self.v_offset
        f = self.nodes.new("NodeFrame")
        
        f.name = f.label = self.textures_type
        f.location = (fx, fy)
        f.height = 580
        f.width = 780
        f.use_custom_color = True
        f.color = 0.25, 0.25, 0.25
        
        #print(fx, fy, self.textures_type)
    
        t_offset = 600
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
            if None == image_path:
                #raise DebugException(f"Unknown Projection {texture.projection}")
                return
    
            i = self.nodes.new("ShaderNodeTexImage")
    
            basename = os.path.basename(image_path)
            image = bpy.data.images.get(basename)
            if None == image:
                image = bpy.data.images.load(image_path)
            i.image = image
            i.location = (dx+300, dy-300+t_offset)
            
    #             # projection
    #             # 0 == planar
    #             # 1 == Cylindrical
    #             # 2 == Spherical
    #             # 3 == Cubic
    #             # 4 == Front
    #             # 5 == UV
    #             if not 5 == texture.projection:
    #                 #raise DebugException(f"Unknown Projection {texture.projection}")
    #                 pass
            self.node_output = i.outputs["Color"]
            if 5 == texture.projection:
                uvname = texture.uvname
                if not isinstance(uvname, str):
                    raise DebugException("Unknown UV")
    
                u = self.nodes.new("ShaderNodeUVMap")
                u.uv_map = uvname
                u.location = (dx+20, dy-300+t_offset)
                self.m.mat.node_tree.links.new(u.outputs["UV"], i.inputs["Vector"])
        elif "PROC" == texture.type:
            #raise DebugException(f"Unsupported type {texture.type}")
            pass
        elif "GRAD" == texture.type:
            #raise DebugException(f"Unsupported type {texture.type}")
            pass
        else:
            raise DebugException(f"Unsupported type {texture.type}")
    
        #exit()
    
def lwo2cycles(surf_data):
    cy = cymat(surf_data)            
    return cy.m
