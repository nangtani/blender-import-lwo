import bpy
import copy
from lwo_helper import blCopy

def read_file(infile):
    print(f"Reading file: {infile}")

    bpy.ops.wm.open_mainfile(filepath=infile)

    o0 = {}
    o0['objects'] = {}
    for k in bpy.data.objects.keys():
        j = bpy.data.objects[k].copy()
        o0['objects'][k] = blCopy(j, bpy.data.objects[k].name)
        bpy.data.objects.remove(j)
        #o0['objects'][k].pprint()

#     o0['meshes'] = {}
#     for k in bpy.data.meshes.keys():
#         j = bpy.data.meshes[k].copy()
#         o0['meshes'][k] = blCopy(j, bpy.data.meshes[k].name)
#         bpy.data.meshes.remove(j)
#         #o0['meshes'][k].pprint()
    
    o0['textures'] = {}
    for k in bpy.data.textures.keys():
        j = bpy.data.textures[k].copy()
        o0['textures'][k] = blCopy(j, bpy.data.textures[k].name)
        bpy.data.textures.remove(j)
        #o0['textures'][k].pprint()
    
    o0['materials'] = {}
    #print(bpy.data.materials.keys())
    for k in bpy.data.materials.keys():
        j = bpy.data.materials[k].copy()
        o0['materials'][k] = blCopy(j, bpy.data.materials[k].name)
        bpy.data.materials.remove(j)
        o0['materials'][k].pprint()

    o0['images'] = {}
    #print(bpy.data.images.keys())
    for k in bpy.data.images.keys():
        j = bpy.data.images[k].copy()
        o0['images'][k] = blCopy(j, bpy.data.images[k].name)
        bpy.data.images.remove(j)
        o0['images'][k].pprint()
    
#     bpy.ops.wm.save_as_mainfile(filepath=infile)
#     bpy.ops.wm.open_mainfile(filepath=infile)
# 
#     bpy.ops.wm.open_mainfile(filepath=infile)
#     #print(j)
#     o0[x].pprint()
    

def main(infile):
    read_file(infile)



if __name__ == "__main__":
    infile = "tests/ref_blend/box1.lwo.blend"
    main(infile)
