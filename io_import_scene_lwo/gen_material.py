import os
import bpy
#from .NodeArrange import nodemargin, ArrangeNodesOp, values

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
