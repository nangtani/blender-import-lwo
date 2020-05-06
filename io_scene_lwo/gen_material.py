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
from .bpy_debug import DebugException

# from .NodeArrange import nodemargin, ArrangeNodesOp, values


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


def lwo2cycles(surf_data):
    m = _material(surf_data.name)
    mat_name = surf_data.name

    m.smooth = surf_data.smooth
    m.mat = bpy.data.materials.new(mat_name)
    m.mat.use_nodes = True
    nodes = m.mat.node_tree.nodes
    surf_data.lwoprint()
    n = nodes["Material Output"]
    if (2, 80, 0) < bpy.app.version:
        pass
    else:  # else bpy.app.version
        m.mat.diffuse_color = surf_data.colr[:]
        d = nodes.new("ShaderNodeBsdfPrincipled")
        m.mat.node_tree.links.new(d.outputs["BSDF"], n.inputs["Surface"])
        nodes.remove(nodes["Diffuse BSDF"])
    # endif

    color = (surf_data.colr[0], surf_data.colr[1], surf_data.colr[2], surf_data.diff)

    d = nodes["Principled BSDF"]
    d.inputs[0].default_value = color

    #     print(d.parent)
    #     print(m.parent)
    #     d.parent = m
    #     #d.set_parent(m)
    #     #print(dir(d))
    #     print(d.parent)
    #     print(m.parent)

    for textures_type, textures in surf_data.textures.items():
        for texture in textures:
            if not textures_type == "COLR":
                continue

            image_path = texture.image
            if None == image_path:
                continue

            c = nodes.new("ShaderNodeRGB")
            c.outputs[0].default_value = color

            i = nodes.new("ShaderNodeTexImage")

            basename = os.path.basename(image_path)
            image = bpy.data.images.get(basename)
            if None == image:
                image = bpy.data.images.load(image_path)
            i.image = image
            
            #m.mat.node_tree.links.new(i.outputs["Color"], d.inputs["Base Color"])
            
            uvname = texture.uvname
            if not isinstance(uvname, str):
                raise DebugException("Unknown UV")
            else:
                u = nodes.new("ShaderNodeUVMap")
                u.uv_map = uvname
                m.mat.node_tree.links.new(u.outputs["UV"], i.inputs["Vector"])

            mix = nodes.new("ShaderNodeMixRGB")
            #mix.Mix = 1.0
            
            mix.inputs[0].default_value = texture.opac
            m.mat.node_tree.links.new(c.outputs["Color"], mix.inputs["Color1"])
            m.mat.node_tree.links.new(i.outputs["Color"], mix.inputs["Color2"])
            m.mat.node_tree.links.new(mix.outputs["Color"], d.inputs["Base Color"])

            n.location = (0.0, 300.0)
            d.location = (-300.0, 300.0)
            mix.location = (-600.0, 300.0)
            c.location = (-900.0, 300.0)
            
            i.location = (-900.0, 000.0)
            u.location = (-1200.0, 000.0)
            
            #print(bpy.data.uv_layers)
            
#             print(n.location)
#             print(d.location)
#             print(i.location)

    # ["Principled BSDF"] = 245
    # ["ShaderNodeTexImage"] = 245
    #     #nodes.update()
    #     v = values
    #     v.mat_name = mat_name
    #
    #     bpy.types.Scene.nodemargin_x = v.margin_x
    #     bpy.types.Scene.nodemargin_y = v.margin_y
    #     bpy.types.Scene.node_center  = True
    #
    #     N = ArrangeNodesOp
    #     N.nodemargin2(v, bpy.context)

    return m
