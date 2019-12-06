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

bl_info = {
    "name": "Import LightWave Objects",
    "author": "Ken Nign (Ken9), Gert De Roost and Dave Keeshan",
    "version": (1, 4, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > LightWave Object (.lwo)",
    "description": "Imports a LWO file including any UV, Morph and Color maps. "
    "Can convert Skelegons to an Armature.",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
    "Scripts/Import-Export/LightWave_Object",
    "category": "Import-Export",
}

# Copyright (c) Ken Nign 2010
# ken@virginpi.com
#
# Version 1.3 - Aug 11, 2011
#
# Loads a LightWave .lwo object file, including the vertex maps such as
# UV, Morph, Color and Weight maps.
#
# Will optionally create an Armature from an embedded Skelegon rig.
#
# Point orders are maintained so that .mdds can exchanged with other
# 3D programs.
#
#
# Notes:
# NGons, polygons with more than 4 points are supported, but are
# added (as triangles) after the vertex maps have been applied. Thus they
# won't contain all the vertex data that the original ngon had.
#
# Blender is limited to only 8 UV Texture and 8 Vertex Color maps,
# thus only the first 8 of each can be imported.
#
# History:
#
# 1.3 Fixed CC Edge Weight loading.
#
# 1.2 Added Absolute Morph and CC Edge Weight support.
#     Made edge creation safer.
# 1.0 First Release


import os

import bpy
import bmesh
import mathutils
from mathutils.geometry import tessellate_polygon
from pprint import pprint

from .lwoObject import lwoObject
#from .NodeArrange import nodemargin, ArrangeNodesOp, values

def draw(self, context):
    self.layout.label("Hello World")

# scn = bpy.context.scene
# row = layout.row()
# row.prop(scn.ignit_panel, "screen_path")  # <-- just for display purposes
# row.operator("macbook_controller.identifier_file_selector", text="", icon='FILE')

def load_lwo(
    filename,
    context,
    ADD_SUBD_MOD=True,
    LOAD_HIDDEN=False,
    SKEL_TO_ARM=True,
):
    """Read the LWO file, hand off to version specific function."""
    #bpy.context.object = {}
    #bpy.context.object["ImportLwo"] = {}
    lwo = lwoObject(filename)
    lwo.search_paths.extend([
        "dirpath",
        "dirpath/images",
        "dirpath/..",
        "dirpath/../images",
#        "dirpath/../../../Textures",
    ])
    lwo.read(ADD_SUBD_MOD, LOAD_HIDDEN, SKEL_TO_ARM)
    
    return lwo
    


def create_mappack(data, map_name, map_type):
    """Match the map data to faces."""
    pack = {}

    def color_pointmap(map):
        for fi in range(len(data.pols)):
            if fi not in pack:
                pack[fi] = []
            for pnt in data.pols[fi]:
                if pnt in map:
                    pack[fi].append(map[pnt])
                else:
                    pack[fi].append((1.0, 1.0, 1.0))

    def color_facemap(map):
        for fi in range(len(data.pols)):
            if fi not in pack:
                pack[fi] = []
                for p in data.pols[fi]:
                    pack[fi].append((1.0, 1.0, 1.0))
            if fi in map:
                for po in range(len(data.pols[fi])):
                    if data.pols[fi][po] in map[fi]:
                        pack[fi].insert(po, map[fi][data.pols[fi][po]])
                        del pack[fi][po + 1]

    if map_type == "COLOR":
        # Look at the first map, is it a point or face map
        if "PointMap" in data.colmaps[map_name]:
            color_pointmap(data.colmaps[map_name]["PointMap"])

        if "FaceMap" in data.colmaps[map_name]:
            color_facemap(data.colmaps[map_name]["FaceMap"])

    return pack


def build_armature(layer_data, bones):
    """Build an armature from the skelegon data in the mesh."""
    print("Building Armature")

    # New Armatures include a default bone, remove it.
    bones.remove(bones[0])

    # Now start adding the bones at the point locations.
    prev_bone = None
    for skb_idx in range(len(layer_data.bones)):
        if skb_idx in layer_data.bone_names:
            nb = bones.new(layer_data.bone_names[skb_idx])
        else:
            nb = bones.new("Bone")

        nb.head = layer_data.pnts[layer_data.bones[skb_idx][0]]
        nb.tail = layer_data.pnts[layer_data.bones[skb_idx][1]]

        if skb_idx in layer_data.bone_rolls:
            xyz = layer_data.bone_rolls[skb_idx].split(" ")
            vec = mathutils.Vector((float(xyz[0]), float(xyz[1]), float(xyz[2])))
            quat = vec.to_track_quat("Y", "Z")
            nb.roll = max(quat.to_euler("YZX"))
            if nb.roll == 0.0:
                nb.roll = min(quat.to_euler("YZX")) * -1
            # YZX order seems to produce the correct roll value.
        else:
            nb.roll = 0.0

        if prev_bone is not None:
            if nb.head == prev_bone.tail:
                nb.parent = prev_bone

        nb.use_connect = True
        prev_bone = nb

def lwo2BI(lwo, surf_key, use_existing_materials):
    surf_data = lwo.surfs[surf_key]
    #bl_mat = None
    #mat_name = lwo.surfs[surf_key].name
    #textures = lwo.surfs[surf_key].textures
    if use_existing_materials:
        surf_data.bl_mat = bpy.data.materials.get(surf_data.name)
#     else:
#         surf_data.bl_mat = None

    if (2, 80, 0) < bpy.app.version:
        #return # FIXME
        raise Exception("Blender Internal has been removed")
    # endif
    if None == surf_data.bl_mat:
        surf_data.bl_mat = bpy.data.materials.new(surf_data.name)
        surf_data.bl_mat.diffuse_color = surf_data.colr[:]
        surf_data.bl_mat.diffuse_intensity = surf_data.diff
        surf_data.bl_mat.emit = surf_data.lumi
        surf_data.bl_mat.specular_intensity = surf_data.spec
        if surf_data.refl != 0.0:
            surf_data.bl_mat.raytrace_mirror.use = True
        surf_data.bl_mat.raytrace_mirror.reflect_factor = surf_data.refl
        surf_data.bl_mat.raytrace_mirror.gloss_factor = 1.0 - surf_data.rblr
        if surf_data.tran != 0.0:
            surf_data.bl_mat.use_transparency = True
            surf_data.bl_mat.transparency_method = "RAYTRACE"
        surf_data.bl_mat.alpha = 1.0 - surf_data.tran
        surf_data.bl_mat.raytrace_transparency.ior = surf_data.rind
        surf_data.bl_mat.raytrace_transparency.gloss_factor = 1.0 - surf_data.tblr
        surf_data.bl_mat.translucency = surf_data.trnl
        surf_data.bl_mat.specular_hardness = (
            int(4 * ((10 * surf_data.glos) * (10 * surf_data.glos))) + 4
        )
        
        for textures_type, textures in surf_data.textures.items():
            for texture in textures:
                if not textures_type == "COLR":
                    continue
                tex_slot = surf_data.bl_mat.texture_slots.add()
                image_path = texture.clip['new_path']
                if None == image_path:
                    continue
                
                #print(image_path)
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
                if not (texture.enab):
                    tex_slot.use_textures[ci - 1] = False
        
        for texture in surf_data.textures_5:
            tex_slot = surf_data.bl_mat.texture_slots.add()
            tex = bpy.data.textures.new(os.path.basename(texture.path), "IMAGE")
            if not (bpy.data.images.get(texture.path)):
                image = bpy.data.images.load(texture.path)
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

def lwo2cycles(lwo, surf_key, use_existing_materials):
    surf_data = lwo.surfs[surf_key]
    mat = None
    mat_name = surf_data.name
    
    if use_existing_materials:
        mat = bpy.data.materials.get(mat_name)
    
    if None == mat:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        m = nodes['Material Output']
        if (2, 80, 0) < bpy.app.version:
            pass
        else: # else bpy.app.version
            mat.diffuse_color = surf_data.colr[:]
            d = nodes.new('ShaderNodeBsdfPrincipled')
            mat.node_tree.links.new(d.outputs['BSDF'], m.inputs['Surface']) 
            nodes.remove(nodes['Diffuse BSDF'])
        # endif
                   
        color = (surf_data.colr[0], surf_data.colr[1], surf_data.colr[2], surf_data.diff)
        #surf_data.diff = 0 == black
        #print(color)
        #print(surf_data.diff, surf_data.tran)
        d = nodes['Principled BSDF']
        d.inputs[0].default_value = color
        
#         print(d.parent)
#         print(m.parent)
#         d.parent = m
#         #d.set_parent(m)
#         #print(dir(d))
#         print(d.parent)
#         print(m.parent)

        for textures_type, textures in surf_data.textures.items():
            for texture in textures:
                if not textures_type == "COLR":
                    continue

                #print(texture.clip, texture.lwoprint())
                image_path = texture.clip['new_path']
                if None == image_path:
                    continue
    
                basename = os.path.basename(image_path)
                image = bpy.data.images.get(basename)
                if None == image:
                    image = bpy.data.images.load(image_path)
                i = nodes.new('ShaderNodeTexImage')
                i.image = image
                #print(ci, image)

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
    
    surf_data.bl_mat = mat

def build_materials(lwo, use_existing_materials):
    print(f"Adding {len(lwo.surfs)} Materials")

    renderer = bpy.context.scene.render.engine
    for surf_key in lwo.surfs:
        if 'CYCLES' == renderer or 'BLENDER_EEVEE' == renderer or 'BLENDER_WORKBENCH' == renderer:
            surf_data = lwo2cycles(lwo, surf_key, use_existing_materials)
        else:
            surf_data = lwo2BI(lwo, surf_key, use_existing_materials)


def build_objects(lwo, use_existing_materials):
    """Using the gathered data, create the objects."""
    ob_dict = {}  # Used for the parenting setup.
    
    build_materials(lwo, use_existing_materials)

    # Single layer objects use the object file's name instead.
    if len(lwo.layers) and lwo.layers[-1].name == "Layer 1":
        lwo.layers[-1].name = lwo.name
        print(f"Building '{lwo.name}' Object")
    else:
        print(f"Building {len(lwo.layers)} Objects")

    # Before adding any meshes or armatures go into Object mode.
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")

    for layer_data in lwo.layers:
        face_edges = []
        me = bpy.data.meshes.new(layer_data.name)
        me.from_pydata(layer_data.pnts, face_edges, layer_data.pols)
#         print(dir(me))
        print(layer_data.pnts)
        print(layer_data.pols)
        print(me.vertices)
        print(me.edges)
        print(me.polygons)
        #me.polygons.add(1)
        
#         print(me.tessfaces)
#         me.calc_tessface()
#         print(me.tessfaces)
#         
        print(dir(me.vertices[0]))
        print(me.vertices[0].co)
        print(me.vertices[1].co)
#         print(me.polygons[0].vertices)
#         for v in me.polygons[0].vertices:
#             print(v)
 
        print(me.edges[0].vertices[0], me.edges[0].vertices[1])
        print(me.edges[1].vertices[0], me.edges[1].vertices[1])
        print(dir(me.edges[0]))
        #bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        print(me.vertices)
        print(me.edges)
        print(me.polygons)
        
#         me_old = bpy.data.meshes.new(layer_data.name)
#         me_old.vertices.add(len(layer_data.pnts))
#         me_old.tessfaces.add(len(layer_data.pols))
#         print(me_old.vertices)
#         print(me_old.tessfaces)
#         raise

#         if (2, 80, 0) < bpy.app.version:
#             pass # FIXME
# #             print(me.loop_triangle)
# #             me.loop_triangles.add(len(layer_data.pols))
#         else:
#             #print("tessfaces.add", len(layer_data.pols))
#             #print(layer_data.pols)
#             me.tessfaces.add(len(layer_data.pols))
#         # for vi in range(len(layer_data.pnts)):
#         #     me.vertices[vi].co= laye  r_data.pnts[vi]
# 
#         # faster, would be faster again to use an array
#         me.vertices.foreach_set("co", [axis for co in layer_data.pnts for axis in co])
# 
#         edges = []  # Holds the FaceIdx of the 2-point polys.
#         for fi, fpol in enumerate(layer_data.pols):
#             fpol.reverse()  # Reversing gives correct normal directions
#             # PointID 0 in the last element causes Blender to think it's un-used.
#             if fpol[-1] == 0:
#                 fpol.insert(0, fpol[-1])
#                 del fpol[-1]
# 
#             vlen = len(fpol)
#             if vlen == 3 or vlen == 4:
#                 pass
# #                 if (2, 80, 0) < bpy.app.version:
# #                     pass # FIXME
# #                 else:
# #                     for i in range(vlen):
# #                         me.tessfaces[fi].vertices_raw[i] = fpol[i]
#             elif vlen == 2:
#                 edges.append(fi)
#             elif vlen != 1:
#                 print(vlen)
#                 ngons[fi] = fpol  # Deal with them later

        ngons = {}  # To keep the FaceIdx consistent, handle NGons later.
        for fi, fpol in enumerate(layer_data.pols):
            fpol.reverse()  # Reversing gives correct normal directions
            # PointID 0 in the last element causes Blender to think it's un-used.
            if fpol[-1] == 0:
                fpol.insert(0, fpol[-1])
                del fpol[-1]
             
            vlen = len(fpol)
            if vlen > 4:
                ngons[fi] = fpol  # Deal with them later

        #print(len(ngons))
        
        ob = bpy.data.objects.new(layer_data.name, me)
        if (2, 80, 0) < bpy.app.version:
            scn = bpy.context.collection
            scn.objects.link(ob)
            bpy.context.view_layer.objects.active = ob
            ob.select_set(state=True)
        else:  # else bpy.app.version
            scn = bpy.context.scene
            scn.objects.link(ob)
            scn.objects.active = ob
            ob.select = True
        # endif
        
        ob_dict[layer_data.index] = [ob, layer_data.parent_index]

        # Move the object so the pivot is in the right place.
        ob.location = layer_data.pivot

        # Create the Material Slots and assign the MatIndex to the correct faces.
        mat_slot = 0
        for surf_key in layer_data.surf_tags:
            if lwo.tags[surf_key] in lwo.surfs:
                me.materials.append(lwo.surfs[lwo.tags[surf_key]].bl_mat)

                for fi in layer_data.surf_tags[surf_key]:
                    me.polygons[fi].material_index = mat_slot
                    me.polygons[fi].use_smooth = lwo.surfs[lwo.tags[surf_key]].smooth

                mat_slot += 1

        #bpy.context.object.data.use_auto_smooth = True
        #bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        
        # Create the Vertex Normals.
        if len(layer_data.vnorms) > 0:
            print("Adding Vertex Normals")
            for vi in layer_data.vnorms.keys():
                me.vertices[vi].normal = layer_data.vnorms[vi]

        # Create the Split Vertex Normals.
        if len(layer_data.lnorms) > 0:
            print("Adding Smoothing from Split Vertex Normals")
            for pi in layer_data.lnorms.keys():
                p = me.polygons[pi]
                p.use_smooth = False
                keepflat = True
                for no in layer_data.lnorms[pi]:
                    vn = layer_data.vnorms[no[0]]
                    if (
                        round(no[1], 4) == round(vn[0], 4)
                        or round(no[2], 4) == round(vn[1], 4)
                        or round(no[3], 4) == round(vn[2], 4)
                    ):
                        keepflat = False
                        break
                if not (keepflat):
                    p.use_smooth = True
                # for li in me.polygons[vn[1]].loop_indices:
                #    l = me.loops[li]
                #    if l.vertex_index == vn[0]:
                #        l.normal = [vn[2], vn[3], vn[4]]

        # Create the Vertex Groups (LW's Weight Maps).
        if len(layer_data.wmaps) > 0:
            print(f"Adding {len(layer_data.wmaps)} Vertex Groups")
            for wmap_key in layer_data.wmaps:
                vgroup = ob.vertex_groups.new()
                vgroup.name = wmap_key
                wlist = layer_data.wmaps[wmap_key]
                for pvp in wlist:
                    vgroup.add((pvp[0],), pvp[1], "REPLACE")

        # Create the Shape Keys (LW's Endomorphs).
        if len(layer_data.morphs) > 0:
            print(f"Adding {len(layer_data.morphs)} Shapes Keys")
            ob.shape_key_add("Basis")  # Got to have a Base Shape.
            for morph_key in layer_data.morphs:
                skey = ob.shape_key_add(morph_key)
                dlist = layer_data.morphs[morph_key]
                for pdp in dlist:
                    me.shape_keys.key_blocks[skey.name].data[pdp[0]].co = [
                        pdp[1],
                        pdp[2],
                        pdp[3],
                    ]

        # Create the Vertex Color maps.
        if len(layer_data.colmaps) > 0:
            print(f"Adding {len(layer_data.colmaps)} Vertex Color Maps")
            for cmap_key in layer_data.colmaps:
                map_pack = create_mappack(layer_data, cmap_key, "COLOR")
                me.vertex_colors.new(cmap_key)
                vcol = me.tessface_vertex_colors[-1]
                if not vcol or not vcol.data:
                    break
                for fi in map_pack:
                    if fi > len(vcol.data):
                        continue
                    face = map_pack[fi]
                    colf = vcol.data[fi]

                    if len(face) > 2:
                        colf.color1 = face[0]
                        colf.color2 = face[1]
                        colf.color3 = face[2]
                    if len(face) == 4:
                        colf.color4 = face[3]

        # Create the UV Maps.
        if len(layer_data.uvmaps_vmad) > 0 or len(layer_data.uvmaps_vmap) > 0:
            allmaps = set(list(layer_data.uvmaps_vmad.keys()))
            allmaps = allmaps.union(set(list(layer_data.uvmaps_vmap.keys())))
            print(f"Adding {len(allmaps)} UV Textures")
            if len(allmaps) > 8:
                bm = bmesh.new()
                bm.from_mesh(me)
                for uvmap_key in allmaps:
                    bm.loops.layers.uv.new(uvmap_key)
                bm.to_mesh(me)
                bm.free()
            else:
                for uvmap_key in allmaps:
                    if (2, 80, 0) < bpy.app.version:
                        uvm = me.uv_layers.new()
                    else:  # else bpy.app.version
                        uvm = me.uv_textures.new()
                    # endif
                    uvm.name = uvmap_key
            vertloops = {}
            for v in me.vertices:
                vertloops[v.index] = []
            for l in me.loops:
                vertloops[l.vertex_index].append(l.index)
            for uvmap_key in layer_data.uvmaps_vmad.keys():
                uvcoords = layer_data.uvmaps_vmad[uvmap_key]["FaceMap"]
                uvm = me.uv_layers.get(uvmap_key)
                for pol_id in uvcoords.keys():
                    for pnt_id, (u, v) in uvcoords[pol_id].items():
                        for li in me.polygons[pol_id].loop_indices:
                            if pnt_id == me.loops[li].vertex_index:
                                uvm.data[li].uv = [u, v]
                                break
            for uvmap_key in layer_data.uvmaps_vmap.keys():
                uvcoords = layer_data.uvmaps_vmap[uvmap_key]["PointMap"]
                uvm = me.uv_layers.get(uvmap_key)
                for pnt_id, (u, v) in uvcoords.items():
                    for li in vertloops[pnt_id]:
                        uvm.data[li].uv = [u, v]
        print(len(me.polygons))

#         # Now add the NGons.
#         print("ngons", ngons)
#         if len(ngons) > 0:
#             for ng_key in ngons:
#                 face_offset = len(me.polygons)
#                 ng = ngons[ng_key]
#                 v_locs = []
#                 for vi in range(len(ng)):
#                     v_locs.append(mathutils.Vector(layer_data.pnts[ngons[ng_key][vi]]))
#                 tris = tessellate_polygon([v_locs])
#                 print(tris)
#                 print(len(tris), face_offset)
#                 #me.polygons.add(1)
#                 #me.polygons.add(len(tris))
#                 for tri in tris:
#                     pass
# #                     face = me.polygons[face_offset]
# # #                     face.vertices_raw[0] = ng[tri[0]]
# # #                     face.vertices_raw[1] = ng[tri[1]]
# # #                     face.vertices_raw[2] = ng[tri[2]]
# #                     face.vertices = (ng[tri[0]], ng[tri[1]], ng[tri[2]])
# #                     #face.vertices = (0, 0, 0)
# #                     #print(face.vertices)
# #                     face.material_index = me.polygons[ng_key].material_index
# #                     face.use_smooth = me.polygons[ng_key].use_smooth
# #                     face_offset += 1
# 
# #         # FaceIDs are no longer a concern, so now update the mesh.
# #         has_edges = len(edges) > 0 or len(layer_data.edge_weights) > 0
# #         me.update(calc_edges=has_edges)
# # 
# #         # Add the edges.
# #         edge_offset = len(me.edges)
# #         me.edges.add(len(edges))
# #         for edge_fi in edges:
# #             me.edges[edge_offset].vertices[0] = layer_data.pols[edge_fi][0]
# #             me.edges[edge_offset].vertices[1] = layer_data.pols[edge_fi][1]
# #             edge_offset += 1

        # Apply the Edge Weighting.
        if len(layer_data.edge_weights) > 0:
            for edge in me.edges:
                edge_sa = "{0} {1}".format(edge.vertices[0], edge.vertices[1])
                edge_sb = "{0} {1}".format(edge.vertices[1], edge.vertices[0])
                if edge_sa in layer_data.edge_weights:
                    edge.crease = layer_data.edge_weights[edge_sa]
                elif edge_sb in layer_data.edge_weights:
                    edge.crease = layer_data.edge_weights[edge_sb]

        # Unfortunately we can't exlude certain faces from the subdivision.
        if layer_data.has_subds and lwo.add_subd_mod:
            ob.modifiers.new(name="Subsurf", type="SUBSURF")

        # Should we build an armature from the embedded rig?
        if len(layer_data.bones) > 0 and lwo.skel_to_arm:
            bpy.ops.object.armature_add()
            arm_object = bpy.context.active_object
            arm_object.name = "ARM_" + layer_data.name
            arm_object.data.name = arm_object.name
            arm_object.location = layer_data.pivot
            bpy.ops.object.mode_set(mode="EDIT")
            build_armature(layer_data, arm_object.data.edit_bones)
            bpy.ops.object.mode_set(mode="OBJECT")

        # Clear out the dictionaries for this layer.
        layer_data.bone_names.clear()
        layer_data.bone_rolls.clear()
        layer_data.wmaps.clear()
        layer_data.colmaps.clear()
        layer_data.uvmaps_vmad.clear()
        layer_data.uvmaps_vmap.clear()
        layer_data.morphs.clear()
        layer_data.surf_tags.clear()

        
        # We may have some invalid mesh data, See: [#27916]
        # keep this last!
        if (2, 80, 0) < bpy.app.version:
            print("loop_triangles", me.calc_loop_triangles())
            if not None == me.calc_loop_triangles():
                raise Exception("me.calc_loop_triangles tripped")
#         elxf (2, 80, 0) < bpy.app.version:
#             if not None == me.calc_loop_triangles():
#                 raise Exception("me.calc_loop_triangles tripped")
#             print("loop_triangles", me.calc_loop_triangles())
#             me.update(calc_loop_triangles=True)
        else:  # else bpy.app.version
            print("tessface", me.calc_tessface())
            if not None == me.calc_tessface():
                raise Exception("me.calc_tessface tripped")
            me.update(calc_tessface=True)
        # endif
        
#         if (2, 80, 0) < bpy.app.version:
#             pass
#             #me.update(calc_loop_triangles=True)
#             #me.update(calc_edges=True)
#             #me.update(calc_edges_loose=True)
#         else:  # else bpy.app.version
#             me.update(calc_tessface=True)
#         # endif

        print(f"Validating mesh: {me.name}...")
        #me.validate(verbose=True)
        me.validate()
        #print("1", me.validate())
        
        # Texture slots have been removed from 2.80, is there a corresponding any thing?
        # Create the 3D View visualisation textures.
        if 'CYCLES' == bpy.context.scene.render.engine or 'BLENDER_EEVEE' == bpy.context.scene.render.engine:
            pass
        else:
            for tf in me.polygons:
                tex_slots = me.materials[tf.material_index].texture_slots
                for ts in tex_slots:
                    if ts:
                        if None == tex_slots[0].texture:
                            continue
                        
                        image = tex_slots[0].texture.image
                        for lay in me.tessface_uv_textures:
                            lay.data[tf.index].image = image
                        break

        print("done!")

    # With the objects made, setup the parents and re-adjust the locations.
    if len(ob_dict.keys()) > 1:
        empty = bpy.data.objects.new(name=lwo.name + "_empty", object_data=None)
        if (2, 80, 0) < bpy.app.version:
            bpy.context.collection.objects.link(empty)
        else:  # else bpy.app.version
            bpy.context.scene.objects.link(empty)
        # endif
    for ob_key in ob_dict:
        if ob_dict[ob_key][1] != -1 and ob_dict[ob_key][1] in ob_dict:
            parent_ob = ob_dict[ob_dict[ob_key][1]]
            ob_dict[ob_key][0].parent = parent_ob[0]
            ob_dict[ob_key][0].location -= parent_ob[0].location
        elif len(ob_dict.keys()) > 1:
            ob_dict[ob_key][0].parent = empty

    if (2, 80, 0) < bpy.app.version:
        bpy.context.view_layer.update()
    else:  # else bpy.app.version
        bpy.context.scene.update()
    # endif

    print("Done Importing LWO File")


from bpy.props import StringProperty, BoolProperty

from bpy_extras.io_utils import ImportHelper

class IdentifierFileSelector(bpy.types.Operator, ImportHelper):
    bl_idname = "open.file_selector"
    bl_label = "Select Path"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        fdir = self.properties.filepath
        
        return{'FINISHED'}
        
class OpenBrowser(bpy.types.Operator):
    bl_idname = "open.browser"
    bl_label = "Select Path"
    bl_options = {"REGISTER", "UNDO"}

    directory = StringProperty(subtype="DIR_PATH") 
    cancel_search = BoolProperty(
        name="Cancel Search",
        description="If no further images are to be found",
        default=False,
    )

#     def draw(self, context):
#         layout = self.layout
#         scn = context.scene
#         
#         #UI
#         col = layout.column()
#         row = col.row(align=True)
#         row.prop(scn.io_import_scene_lwo, 'directory', text='directory:')
#         row.operator("scn.open.browser", icon="FILE_FOLDER", text="")
    
    def execute(self, context):
        #display = "dirpath=" + self.directory  
        print(self.directory)  
        #context.scene.ignit_panel.screen_path = self.properties.filepath
        #print(dir(context.object))
        #print(dir(bpy.context.object))
        #bpy.context.object["ImportLwo"] = {}
        #bpy.context.object["ImportLwo"]["directory"] = self.directory
        #print(bpy.context.object.keys(), self)
        #bpy.data.scenes["Scene"].set("ImportLwo", self.directory)
        #print()
        context.scene.lwo_directory = "y" + self.directory
        bpy.types.Scene.lwo_directory = "xx"
        #context.scene.lwo_directoryx = "x" + self.directory
        print("lwo_directory", context.scene.lwo_directory)
        #print("lwo_directoryx", context.scene.lwo_directoryx)
        return {'FINISHED'}

    def invoke(self, context, event): 
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}  


class IMPORT_OT_lwo(bpy.types.Operator):
    """Import LWO Operator"""

    bl_idname = "import_scene.lwo"
    bl_label = "Import LWO"
    bl_description = "Import a LightWave Object file"
    bl_options = {"REGISTER", "UNDO"}
    
    bpy.types.Scene.lwo_directory = StringProperty()


    if (2, 80, 0) < bpy.app.version:
        filepath: StringProperty(
            name="File Path",
            description="Filepath used for importing the LWO file",
            maxlen=1024,
            default="",
        )
    
        ADD_SUBD_MOD: BoolProperty(
            name="Apply SubD Modifier",
            description="Apply the Subdivision Surface modifier to layers with Subpatches",
            default=True,
        )
        LOAD_HIDDEN: BoolProperty(
            name="Load Hidden Layers",
            description="Load object layers that have been marked as hidden",
            default=False,
        )
        SKEL_TO_ARM: BoolProperty(
            name="Create Armature",
            description="Create an armature from an embedded Skelegon rig",
            default=True,
        )
        USE_EXISTING_MATERIALS: BoolProperty(
            name="Use Existing Materials",
            description="Use existing materials if a material by that name already exists",
            default=False,
        )
    else:  # else bpy.app.version
        filepath = StringProperty(
            name="File Path",
            description="Filepath used for importing the LWO file",
            maxlen=1024,
            default="",
        )
    
        ADD_SUBD_MOD = BoolProperty(
            name="Apply SubD Modifier",
            description="Apply the Subdivision Surface modifier to layers with Subpatches",
            default=True,
        )
        LOAD_HIDDEN = BoolProperty(
            name="Load Hidden Layers",
            description="Load object layers that have been marked as hidden",
            default=False,
        )
        SKEL_TO_ARM = BoolProperty(
            name="Create Armature",
            description="Create an armature from an embedded Skelegon rig",
            default=True,
        )
        USE_EXISTING_MATERIALS = BoolProperty(
            name="Use Existing Materials",
            description="Use existing materials if a material by that name already exists",
            default=False,
        )
    # endif
    
    def execute(self, context):
        #context.scene.lwo_directory = ""
        lwo = load_lwo(
            self.filepath,
            context,
            self.ADD_SUBD_MOD,
            self.LOAD_HIDDEN,
            self.SKEL_TO_ARM,
        )
    
#         #bpy.ops.open.browser('INVOKE_DEFAULT')
#         #bpy.ops.open.file_selector('EXEC_DEFAULT')
#         bpy.ops.open.browser('INVOKE_DEFAULT')
#         
#         print("xexd", context.scene.lwo_directory)
#         context.scene.lwo_directory = "tree"
#         #print("xfxd", context.scene.lwo_directoryx)
#         #print("12", bpy.types.Object.lwo_directoryx)
#         #print("xexd", context.scene.directory)
#         #print("k", OpenBrowser)
#         #print("j", OpenBrowser.directory)
#         lwo.resolve_clips()
#         print("swer", context.scene.lwo_directory)

        # With the data gathered, build the object(s).
        build_objects(lwo,  self.USE_EXISTING_MATERIALS)
        return {"FINISHED"}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}


def menu_func(self, context):
    self.layout.operator(IMPORT_OT_lwo.bl_idname, text="LightWave Object (.lwo)")

classes = (IMPORT_OT_lwo, OpenBrowser, IdentifierFileSelector,)

def register():
    if (2, 80, 0) < bpy.app.version:
        for cls in classes:
            bpy.utils.register_class(cls)

        bpy.types.TOPBAR_MT_file_import.append(menu_func)
    else:  # else bpy.app.version
        #bpy.types.Scene.lwo_directoryx = StringProperty()
        bpy.utils.register_module(__name__)
        bpy.types.INFO_MT_file_import.append(menu_func)
    # endif

def unregister():
    if (2, 80, 0) < bpy.app.version:
        for cls in classes:
            bpy.utils.unregister_class(cls)

        bpy.types.TOPBAR_MT_file_import.remove(menu_func)
    else:  # else bpy.app.version
        bpy.utils.unregister_module(__name__)
        #del bpy.types.Object.lwo_directoryx
        bpy.types.INFO_MT_file_import.remove(menu_func)
    # endif

if __name__ == "__main__":
    register()
