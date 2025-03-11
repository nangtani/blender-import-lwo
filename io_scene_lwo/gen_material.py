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

    color = (surf_data.colr[0], surf_data.colr[1], surf_data.colr[2], surf_data.diff)
    # surf_data.diff = 0 == black
    # print(color)
    # print(surf_data.diff, surf_data.tran)
    d = nodes["Principled BSDF"]
    d.inputs[0].default_value = color

    for textures_type, textures in surf_data.textures.items():
        for texture in textures:
            if not textures_type == "COLR":
                continue

            image_path = texture.image
            if image_path is None:
                continue

            basename = os.path.basename(image_path)
            image = bpy.data.images.get(basename)
            if image is None:
                image = bpy.data.images.load(image_path)
            i = nodes.new("ShaderNodeTexImage")
            i.image = image
            # print(ci, image)

    return m
