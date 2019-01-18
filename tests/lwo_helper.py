import os
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
#     elif x is None or \
#        isinstance(x, str) or \
#        isinstance(x, int) or \
#        isinstance(x, float) or \
#        isinstance(x, list) or \
#        isinstance(x, tuple) or \
#        isinstance(x, Quaternion) or \
#        isinstance(x, Euler) or \
#        isinstance(x, Matrix) or \
#        isinstance(x, Vector):
#         if not x == y:    
#             fail = True
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
    try:
        y1 = getattr(y,a)
    except:
        print("ERROR: y1 does not have attribute: {0}".format(a))
    
    if 'active_material' == a or \
       'material_slots' == a:
        #print(x1, True)
        pass
    else:
        fail = compare_obj(x1, y1)
        #print(a, fail, x1)
    
    if fail:
        error_count += 1
        print("ERROR: Attributes do not match: {0} - {1} - {2}".format(a, x1, y1))
    
    return error_count

class deepCopy:
    def __repr__(self):
        return self.name
    
    def deepcopy(self, m):
        for k in dir(m):
           setattr(self, k, getattr(m,k))


def diff_files(outfile0, outfile1, error_count=0):
    print("Diffing files!")
    if os.path.isfile(outfile1):
        print("Reference blend present: {0}".format(outfile1))
    else:
        print("No reference blend present: {0}".format(outfile1))
        exit()
    
    m1 = None
    
    bpy.ops.wm.open_mainfile(filepath=outfile0)
    o0 = {}
    for k in bpy.data.objects.keys():
        o0[k] = deepCopy()
        j = bpy.ops.object.add()
        j = bpy.data.objects[k].copy()
        o0[k].deepcopy(bpy.data.objects[k].copy())
    #print(o0)
    
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
        attr_list.remove('MeasureGenerator')
        attr_list.remove('__ge__')
        attr_list.remove('__gt__')
        attr_list.remove('__hash__')
        attr_list.remove('__eq__')
        attr_list.remove('__le__')
        attr_list.remove('__lt__')
        attr_list.remove('__ne__')
        attr_list.remove('__init__')
        attr_list.remove('__repr__')
        attr_list.remove('__reduce__')
        attr_list.remove('__reduce_ex__')
        attr_list.remove('__getattribute__')
        attr_list.remove('__dir__')
        attr_list.remove('__doc__')
        attr_list.remove('__module__')
        attr_list.remove('__slots__')
        attr_list.remove('__dict__')
        attr_list.remove('__delattr__')
        attr_list.remove('__setattr__')
        attr_list.remove('__str__')
        attr_list.remove('__sizeof__')
        attr_list.remove('__format__')
        for a in attr_list:
            error_count = compare_bpy(a, x, y, error_count)
            #if not 0 == error_count:
                #break
        print("Test completed with {0} errors".format(error_count))
        
