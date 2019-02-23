import os
import re
#import time
import copy
import bpy
from mathutils import Vector, Matrix, Euler, Quaternion
from pprint import pprint

def delete_everything():
    
    for k in bpy.data.objects.keys():
        try:
            o = bpy.data.objects[k]
        except KeyError:
            continue
            #print(o)
        if (2, 80, 0) < bpy.app.version:
            o.select_get()
        else:
            o.select = True
        bpy.ops.object.delete()

    for k in bpy.data.textures.keys():
        j = bpy.data.textures[k]
        bpy.data.textures.remove(j)

    for k in bpy.data.materials.keys():
        j = bpy.data.materials[k]
        bpy.data.materials.remove(j)

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
        raise Exception(f"Attribute <{x}> of Unknown type {t}")
        x = None
    return x
    
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


def setup_lwo(infile):
    print("Setting up!")
    if re.search("src_lwo", infile):
        name = infile.split("src_lwo/")[-1]
    else:
        name = os.path.basename(infile)
    
    render = bpy.context.scene.render.engine.lower()
    dst_path = f"tests/dst_blend/{bpy.app.version[0]}.{bpy.app.version[1]}"
    ref_path = f"tests/ref_blend/{bpy.app.version[0]}.{bpy.app.version[1]}"

    outfile0 = f"{dst_path}/{render}/{name}.blend"
    outfile1 = f"{ref_path}/{render}/{name}.blend"

    delete_everything()

    if os.path.isfile(outfile0):
        os.remove(outfile0)

    os.path.split(outfile0)[0]
    if not os.path.exists(os.path.split(outfile0)[0]):
        os.makedirs(os.path.split(outfile0)[0])
    if not os.path.exists(os.path.split(outfile1)[0]):
        os.makedirs(os.path.split(outfile1)[0])

    return (outfile0, outfile1)


# def compare_obj(x, y):
#     fail = False
# 
#     if (
#         str(x).startswith("<bpy_boolean")
#         or str(x).startswith("<bpy_int")
#         or str(x).startswith("<bpy_float")
#         or str(x).startswith("<bpy_collection")
#     ):
#         if not len(x) == len(y):
#             fail = True
#         else:
#             for i in range(len(x)):
#                 fail = compare_obj(x[i], y[i])
#     elif str(x).startswith("<bpy_func"):
#         # print(x1, True)
#         return None
#     elif str(x).startswith("<bpy_struct"):
#         # print(a, x1)
#         return None
#     elif str(x).startswith("<bound"):
#         # print(a, x1)
#         return True
#     #     elif str(x) == "name":
#     #         #print(a, x1)
#     #         return True
#     else:
#         if not x == y:
#             fail = True
#         # fail = True
# 
#     return fail
# 
# 
# def compare_bpy(a, x, y, error_count=0):
#     from mathutils import Vector, Matrix, Euler, Quaternion
# 
#     fail = False
#     try:
#         x1 = getattr(x, a)
#     except:
#         print("ERROR: x1 does not have attribute: {0}".format(a))
#         assert False
#     try:
#         y1 = getattr(y, a)
#     except:
#         print("ERROR: y1 does not have attribute: {0}".format(a))
#         assert False
# 
#     if "name" == a:
#         x1 = x1.split(".")[0]
#         y1 = y1.split(".")[0]
# 
#     #     if 'active_material' == a or \
#     #        'material_slots' == a:
#     #         #print(x1, True)
#     #         pass
#     #         return(0)
#     #     el
#     if "bound_box" == a:
#         return 0
#     elif "deepcopy" == a:  # this is a method on the class
#         return 0
#     else:
#         fail = compare_obj(x1, y1)
#         # print(a, fail, x1)
# 
#     if fail:
#         error_count += 1
#         print("ERROR: Attributes do not match: {0} - {1} - {2}".format(a, x1, y1))
#         if "color" == a:
#             print(x1, x1[0], x1[1], x1[1], x1[3])
#             print(y1, y1[0], y1[1], y1[1], y1[3])
#         if "material_slots" == a:
#             print(x1)
#             print(y1)
# 
#         assert False
# 
#     return error_count
# 

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
                print(f"<{a}> in not in dst")
            if not x.bl[a] == y.bl[a]:
               print(f"<{a}> is different")
               pprint(x.bl[a])
               pprint(y.bl[a])
               assert False
