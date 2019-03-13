import os
import re
import copy
import zipfile
import shutil
import bpy
from mathutils import Vector, Matrix, Euler, Quaternion
from pprint import pprint

class blCopy:
    
    def __init__(self, m, name):
        self.bl = objToDict(m)
        self.bl["name"] = name
        self.bl.pop("active_material", None) # not really something that can be diffed
        self.bl.pop("select", None) # not really something that can be diffed
    
    def __repr__(self):
        return self.bl_name
        
    def pprint(self):
        pprint(self.bl)

def delete_everything():
    
    for k in bpy.data.objects.keys():
        try:
            o = bpy.data.objects[k]
        except KeyError:
            continue

        if (2, 80, 0) < bpy.app.version:
            o.select_get()
        else:
            o.select = True
        bpy.ops.object.delete()

    for k in bpy.data.textures.keys():
        j = bpy.data.textures[k]
        if (2, 79, 0) < bpy.app.version:
            bpy.data.textures.remove(j)
        else:
            bpy.data.textures.remove(j, do_unlink=True)

    for k in bpy.data.materials.keys():
        j = bpy.data.materials[k]
        if (2, 79, 0) < bpy.app.version:
            bpy.data.materials.remove(j)
        else:
            bpy.data.materials.remove(j, do_unlink=True)

    for k in bpy.data.images.keys():
        j = bpy.data.images[k]
        bpy.data.images.remove(j)


def objToDict(m):
    n = {}
    for k in dir(m):
        if k.startswith("__"):
            continue
        n[k] = copy.deepcopy(checkType(getattr(m, k)))
    return n

def checkType(x):
    stype = (type(None), bool, int, float, tuple, list, str, Vector, Matrix, Euler, Quaternion)
    
    if isinstance(x, bpy.types.bpy_struct):
        i = type(x)
#         if isinstance(x, bpy.types.Material):
#             pass
#             #print(True)
#             print(i, dir(x))
#         elif isinstance(x, bpy.types.MaterialSlot):
#             pass
#             #print(True)
#             print(i, dir(x))
        
        #print(x.items())
#         if hasattr(x, "description"):
#             print(x.base)
#             print(x.description)
#             print(x.name)
#             print(x.nested)
#             print(x.properties[0])
        
        if hasattr(x, "material"):
            #print(True)
            #print("Known", i)
            #print(i)
            i = objToDict(x)
        else:
            pass
            #print(i)
#         try:
# #            print(x.name)
#             print(x.material)
# #             print(x.link)
# #             print(x.bl_rna)
#             print(x.rna_type)
#             #pprint(i)
#         except:
#             pass
        return i
    elif isinstance(x, bpy.types.bpy_func):
        #print(k, x, "bpy.types.bpy_func")
        i = type(x)
        return i
#     elif isinstance(x, type(object)):
#         print(k, x, "bpy.types.bpy_method")
#         i = type(x)
#         return i
#     elif isinstance(x, bpy.types.bpy_prop_array):
#         #print(x, "bpy.types.bpy_prop_array")
#         i = type(x)
#         w = {i: []}
#         for y in x:
#             z = checkType(y)
#             w[i].append(z)
#         return(w)
#     elif isinstance(x, bpy.types.bpy_prop_collection):
#         #print(x, "bpy.types.bpy_prop_collection")
#         i = type(x)
#         w = {i: []}
#         for y in x:
#             z = checkType(y)
#             #print("z", z)
#             w[i].append(z)
#         #print(w)
#         return(w)
    elif isinstance(x, (bpy.types.bpy_prop_array, bpy.types.bpy_prop_collection)):
        #print(x, "bpy.types.bpy_prop_collection")
        i = type(x)
        w = {i: []}
        for y in x:
            z = checkType(y)
            #print("z", z)
            w[i].append(z)
        #print(w)
        return(w)
#     elif isinstance(x, (Vector, Matrix, Euler, Quaternion)):
#         pass
    elif isinstance(x, stype):
        pass
#     elif isinstance(x, type(None)):
#         pass
#     elif isinstance(x, bool):
#         pass
#     elif isinstance(x, int):
#         pass
#     elif isinstance(x, float):
#         pass
#     elif isinstance(x, str):
#         pass
#     elif isinstance(x, tuple):
#         pass
#     elif isinstance(x, list):
#         pass
    else:
        print(x, "Unknown", type(x))
        t = type(x)
        print(t)
        #raise Exception(f"Attribute <{x}> of Unknown type {t}")
        raise Exception("Attribute <{0}> of Unknown type {1}".format(x, t))
        x = None
    return x

def diff_files(outfile0, outfile1, error_count=0):
    print("Diffing files!")
    if os.path.isfile(outfile1):
        print("Reference blend present: {0}".format(outfile1))
    else:
        print("No reference blend present: {0}".format(outfile1))
        assert False
        return

    bpy.ops.wm.open_mainfile(filepath=outfile0)
    o0 = {}
    for k in bpy.data.objects.keys():
        j = bpy.data.objects[k].copy()
        o0[k] = blCopy(j, bpy.data.objects[k].name)
        bpy.data.objects.remove(j)


    bpy.ops.wm.open_mainfile(filepath=outfile1)
    o1 = {}
    for k in bpy.data.objects.keys():
        j = bpy.data.objects[k].copy()
        o1[k] = blCopy(j, bpy.data.objects[k].name)
        bpy.data.objects.remove(j)
        
    for k in o0.keys():
        x = o0[k]
        y = o1[k]
        
        #x.pprint()
        #y.pprint()
        
        for a in x.bl.keys():
            #print(a)
            if not a in y.bl.keys():
                print("<{}> in not in dst".format(a))
            if not x.bl[a] == y.bl[a]:
                print("<{}> is different".format(a))
                pprint(x.bl[a])
                pprint(y.bl[a])
                assert False
