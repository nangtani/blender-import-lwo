import os
import re
import copy
import zipfile
import shutil
import types
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler, Quaternion
from pprint import pprint


class blCopy:
    def __init__(self, m, name, keys=None):
        self.bl = objToDict(m)
        self.bl["name"] = name
        self.bl.pop("active_material", None)  # not really something that can be diffed
        self.bl.pop("select", None)  # not really something that can be diffed

    def __repr__(self):
        return self.bl_name

    def pprint(self):
        pprint(self.bl)


def delete_everything():

    if (2, 79, 0) < bpy.app.version:
        bpy.ops.wm.read_homefile()
    
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
        bpy.data.textures.remove(j)

    for k in bpy.data.materials.keys():
        j = bpy.data.materials[k]
        bpy.data.materials.remove(j)

    for k in bpy.data.images.keys():
        j = bpy.data.images[k]
        bpy.data.images.remove(j)

    for k in bpy.data.meshes.keys():
        j = bpy.data.meshes[k]
        bpy.data.meshes.remove(j)


def objToDict(m):
    n = {}
    for k in dir(m):
        if k.startswith("__") or "group" == k:
            continue
        # print(m, dir(m))
        x = getattr(m, k)
        y = checkType(x)
        n[k] = copy.deepcopy(y)
    return n


def checkType(x):
    stype = (
        type(None),
        bool,
        int,
        float,
        tuple,
        list,
        str,
        Vector,
        Matrix,
        Euler,
        Quaternion,
    )

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

        # print(x.items())
        #         if hasattr(x, "description"):
        #             print(x.base)
        #             print(x.description)
        #             print(x.name)
        #             print(x.nested)
        #             print(x.properties[0])

        if hasattr(x, "material"):
            # print(True)
            # print("Known", i)
            # print(i)
            i = objToDict(x)
        else:
            pass
            # print(i)
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
        # print(k, x, "bpy.types.bpy_func")
        i = type(x)
        return i
    elif isinstance(x, bpy.types.MeshVertex):
        # print(k, x, "bpy.types.MeshVertex")
        # i = type(x)
        return None
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
        # print(x, "bpy.types.bpy_prop_collection")
        i = type(x)
        w = {i: []}
        for y in x:
            z = checkType(y)
            # print("z", z)
            w[i].append(z)
        # print(w)
        return w
    #     elif isinstance(x, (Vector, Matrix, Euler, Quaternion)):
    #         pass
    elif isinstance(x, stype):
        pass
    elif isinstance(x, types.MethodType):
        return None
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


def diff_files(outfile0, outfile1, error_count=0):
    print("Diffing files!")
    if os.path.isfile(outfile1):
        print(f"Reference blend present: {outfile1}")
    else:
        print(f"No reference blend present: {outfile1}")
        assert False
        return

    bpy.ops.wm.open_mainfile(filepath=outfile0)
    o0 = {}
    m0 = {}
    for k in bpy.data.objects.keys():
        j = bpy.data.objects[k].copy()
        o0[k] = blCopy(j, bpy.data.objects[k].name)
        bpy.data.objects.remove(j)
    #     for k in bpy.data.meshes.keys():
    #         j = bpy.data.meshes[k].copy()
    #         m0[k] = blCopy(j, bpy.data.meshes[k].name)
    #         bpy.data.meshes.remove(j)
    n0 = {}
    for k in bpy.data.meshes.keys():
        bm = bmesh.new()
        bm.from_mesh(bpy.data.meshes[k])
        n0[k] = {}
        # print("materials", dir(bm))
        n0[k]["faces"] = len(bm.faces)
        n0[k]["edges"] = len(bm.edges)
        n0[k]["verts"] = len(bm.verts)
        n0[k]["materials"] = len(bpy.data.materials)  # should be independent from mesh
        n0[k]["images"] = len(bpy.data.images)
        bm.free()

    bpy.ops.wm.open_mainfile(filepath=outfile1)
    o1 = {}
    m1 = {}
    for k in bpy.data.objects.keys():
        j = bpy.data.objects[k].copy()
        o1[k] = blCopy(j, bpy.data.objects[k].name)
        bpy.data.objects.remove(j)
    #     for k in bpy.data.meshes.keys():
    #         j = bpy.data.meshes[k].copy()
    #         m1[k] = blCopy(j, bpy.data.meshes[k].name)
    #         bpy.data.meshes.remove(j)
    n1 = {}
    for k in bpy.data.meshes.keys():
        bm = bmesh.new()
        bm.from_mesh(bpy.data.meshes[k])
        n1[k] = {}
        # print("materials", dir(bm))
        n1[k]["faces"] = len(bm.faces)
        n1[k]["edges"] = len(bm.edges)
        n1[k]["verts"] = len(bm.verts)
        n1[k]["materials"] = len(bpy.data.materials)
        n1[k]["images"] = len(bpy.data.images)
        bm.free()

    # pprint(n0)
    # pprint(n1)

    for k in o0.keys():
        x = o0[k]
        y = o1[k]

        # x.pprint()
        # y.pprint()

        for a in x.bl.keys():
            # print(a)
            if not a in y.bl.keys():
                print(f"<{a}> in not in dst")
            if not x.bl[a] == y.bl[a]:
                print(f"<{a}> is different")
                pprint(x.bl[a])
                pprint(y.bl[a])
                assert False

    #     for k in m0.keys():
    #         x = m0[k]
    #         y = m1[k]
    #
    #         for a in x.bl.keys():
    #             #print(a)
    #             if not a in y.bl.keys():
    #                 print(f"<{a}> in not in dst")
    #             if not x.bl[a] == y.bl[a]:
    #                 print(f"<{a}> is different")
    #                 pprint(x.bl[a])
    #                 pprint(y.bl[a])
    #                 assert False

    #         print(x.bl["edges"])
    #         print(y.bl["edges"])
    #         print(x.bl["edges"] == y.bl["edges"])
    #
    #         for j in x.bl["edges"].keys():
    #             print(j)
    #             print(x.bl["edges"][j][0])
    #             print(dir(x.bl["edges"][j][0]))
    #             print(x.bl["edges"][j][0].values)

    if not len(n0.keys()) == len(n1.keys()):
        print("<> different set of mesh keys")
        print(n0.keys())
        print(n1.keys())
        assert False
    for k in n0.keys():
        x = n0[k]
        y = n1[k]
        if not len(x.keys()) == len(y.keys()):
            print("<> different set of keys")
            print(x.keys())
            print(y.keys())
            assert False
        for a, b in x.items():
            if not a in y.keys():
                print(f"<{a}> in not in dst")
            if not x[a] == y[a]:
                print(f"<{a}> is different")
                pprint(x[a])
                pprint(y[a])
                assert False
