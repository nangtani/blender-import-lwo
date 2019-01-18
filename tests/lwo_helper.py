import os
import time
import bpy

def setup_lwo(infile):
    print("Setting up!")
    name = os.path.basename(infile)
    dst_path = "tests/dst_blend"
    ref_path = "tests/ref_blend"
    
    outfile0 = "{0}/{1}.blend".format(dst_path, name)
    outfile1 = "{0}/{1}.blend".format(ref_path, name)
#     for x in bpy.data.objects.keys():
#         print(x)
#         bpy.data.objects[x].select = True
#         bpy.ops.object.delete()
    if 'Camera' in bpy.data.objects.keys():
        bpy.data.objects['Camera'].select = True
        bpy.ops.object.delete()
    if 'Lamp' in bpy.data.objects.keys():
        bpy.data.objects['Lamp'].select = True
        bpy.ops.object.delete()
    if 'Cube' in bpy.data.objects.keys():
        bpy.data.objects['Cube'].select = True
        bpy.ops.object.delete()

    if os.path.isfile(outfile0):
        os.remove(outfile0)
    
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    if not os.path.exists(ref_path):
        os.makedirs(ref_path)

    return(outfile0, outfile1)

def compare_obj(x, y):
    fail = False
    
    if str(x).startswith("<bpy_boolean") or \
       str(x).startswith("<bpy_int") or \
       str(x).startswith("<bpy_float") or \
       str(x).startswith("<bpy_collection"):
        if not len(x) == len(y):
            fail = True
        else:
            for i in range(len(x)):
                fail = compare_obj(x[i], y[i])
    elif str(x).startswith("<bpy_func"):
        #print(x1, True)
        return None
    elif str(x).startswith("<bpy_struct"):
        #print(a, x1)
        return None
    elif str(x).startswith("<bound"):
        #print(a, x1)
        return True
#     elif str(x) == "name":
#         #print(a, x1)
#         return True
    else:
        if not x == y:    
            fail = True
        #fail = True
       
    return fail

def compare_bpy(a, x, y, error_count = 0):
    from mathutils import Vector, Matrix, Euler, Quaternion
    fail = False
    try:
        x1 = getattr(x,a)
    except:
        print("ERROR: x1 does not have attribute: {0}".format(a))
        assert False
    try:
        y1 = getattr(y,a)
    except:
        print("ERROR: y1 does not have attribute: {0}".format(a))
        assert False
    
    if 'name' == a:
        x1 = x1.split(".")[0]
        y1 = y1.split(".")[0]
    
    if 'active_material' == a or \
       'material_slots' == a:
        #print(x1, True)
        pass
        return(0)
    elif 'bound_box' == a:
        return(0)
    elif 'deepcopy' == a:
        return(0)
    else:
        fail = compare_obj(x1, y1)
        #print(a, fail, x1)
    
    if fail:
        error_count += 1
        print("ERROR: Attributes do not match: {0} - {1} - {2}".format(a, x1, y1))
        assert False
    
    return error_count

class deepCopy:
    def __repr__(self):
        return self.name
    
    def deepcopy(self, m):
        for k in dir(m):
            if k.startswith("__"):
                continue
            setattr(self, k, getattr(m,k))


def diff_files(outfile0, outfile1, error_count=0):
    print("Diffing files!")
    if os.path.isfile(outfile1):
        print("Reference blend present: {0}".format(outfile1))
    else:
        print("No reference blend present: {0}".format(outfile1))
        assert False
        return
    
    m1 = None
    
    bpy.ops.wm.open_mainfile(filepath=outfile0)
    o0 = {}
    for k in bpy.data.objects.keys():
        o0[k] = deepCopy()
        j = bpy.ops.object.add()
        j = bpy.data.objects[k].copy()
        o0[k].deepcopy(bpy.data.objects[k].copy())
    #print(o0)
    
    time.sleep(0.25)
    
    bpy.ops.wm.open_mainfile(filepath=outfile1)
    print(j)
    o1 = {}
    for k in bpy.data.objects.keys():
        o1[k] = deepCopy()
        o1[k].deepcopy(bpy.data.objects[k].copy())

    for k in o0.keys():
        x = o0[k]
        y = o1[k]
        #pprint(dir(x))
        #pprint(k)
        attr_list = dir(x)
        for a in attr_list:
            if a.startswith("__"):
                continue
            print(a)
            error_count = compare_bpy(a, x, y, error_count)
            #if not 0 == error_count:
                #break
        #assert False
        print("Test completed with {0} errors".format(error_count))
        
