import os
import sys
import re
import time
import zipfile
import shutil
import bpy

# def mkdir_p(outfile):
#     outfile = re.sub("\\\\", "/", outfile)
#     dirname = os.path.dirname(outfile).split("/")
#     for i in range(len(dirname)):
#         new_path = "/".join(dirname[0:i+1])
#         if not os.path.isdir(new_path):
#             os.mkdir(new_path)

def clean_file(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    
    unique_blender = True
    fix_fstrings = False
    if bpy.app.version <= (2, 79, 0):
        fix_fstrings = True
    
    trim_code = False
    active_print0 = None
    f = open(filename, 'w')
    for line in lines:
        if unique_blender:
            line2 = line
            if re.search("^\s+else", line) and re.search("else bpy.app.version", line):
                active_print0 = not(active_print0)
                line2 = ""
        
            if re.search("endif", line):
                active_print0 = None
                trim_code = False
                line2 = ""
        
            h = re.search("^\s+[el]?if \((\d+), (\d+), (\d+)\) < bpy.app.version", line)
            if h:
                current_blender_rev = (int(h.group(1)), int(h.group(2)), int(h.group(3)))
                trim_code = True
                active_print0 = (current_blender_rev <= bpy.app.version)
                line2 = ""
                #line = re.sub("elif", "if", line)
        
            if trim_code:
                line2 = re.sub("^    ", "", line2)
            if not active_print0 and not active_print0 == None:
                line2 = ""
            line = line2
        
        k = re.search("\"blender\":\s\(\d+, \d+, \d+\)", line)
        if k:
            line = "    \"blender\": {0},\n".format(bpy.app.version)
        
        if re.search("print\(f\"", line) and fix_fstrings:
            line = re.sub("print", "pass ; # print", line)
        f.write(line)
    f.close()

def zip_addon(addon):
    bpy_module = re.sub(".py", "", os.path.basename(os.path.realpath(addon)))
    zfile = os.path.realpath(bpy_module + ".zip")

    print("Zipping addon - {0}".format(bpy_module))
    
    cwd = os.getcwd()
    temp_dir = "tmp"
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)

    shutil.copytree(addon, temp_dir + "/" + addon)
    os.chdir(temp_dir)
    if os.path.isdir("__pycache__"):
        shutil.rmtree("__pycache__")
    zf = zipfile.ZipFile(zfile, "w")
    if os.path.isdir(addon):
        for dirname, subdirs, files in os.walk(addon):
            zf.write(dirname)
            for filename in files:
                filename = os.path.join(dirname, filename)
                clean_file(filename)
                zf.write(filename)
    else:
        clean_file(addon)
        zf.write(addon)
    zf.close()
        
    os.chdir(cwd)
    shutil.rmtree(temp_dir)
    return (bpy_module, zfile)

def change_addon_dir(bpy_module, zfile, addon_dir):
    print("Change addon dir - {0}".format(addon_dir))


    if (2, 80, 0) < bpy.app.version:
        bpy.context.preferences.filepaths.script_directory = addon_dir
        bpy.utils.refresh_script_paths()
        bpy.ops.preferences.addon_install(overwrite=True, filepath=zfile)
        bpy.ops.preferences.addon_enable(module=bpy_module)
    else:
        bpy.context.user_preferences.filepaths.script_directory = addon_dir
        bpy.utils.refresh_script_paths()
        bpy.ops.wm.addon_install(overwrite=True, filepath=zfile)
        bpy.ops.wm.addon_enable(module=bpy_module)


def copy_addon(bpy_module, zfile):
    print("Copying addon - {} {}".format(bpy_module, zfile))

    if (2, 80, 0) < bpy.app.version:
        bpy.ops.preferences.addon_install(overwrite=True, filepath=zfile)
        bpy.ops.preferences.addon_enable(module=bpy_module)
    else:
        bpy.ops.wm.addon_install(overwrite=True, filepath=zfile)
        bpy.ops.wm.addon_enable(module=bpy_module)


def cleanup(addon, bpy_module):
    print("Cleaning up - {}".format(bpy_module))
    if (2, 80, 0) < bpy.app.version:
        bpy.ops.preferences.addon_disable(module=bpy_module)

        # addon_remove does not work correctly in CLI
        # bpy.ops.preferences.addon_remove(module=bpy_module)
        addon_dirs = bpy.utils.script_paths(subdir="addons")
        addon = os.path.join(addon_dirs[-1], addon)
        if os.path.isdir(addon):
            time.sleep(0.1)  # give some time for the disable to take effect
            shutil.rmtree(addon)
        else:
            os.remove(addon)
    else:
        bpy.ops.wm.addon_disable(module=bpy_module)
    
        # addon_remove does not work correctly in CLI
        # bpy.ops.wm.addon_remove(bpy_module=bpy_module)
        addon_dirs = bpy.utils.script_paths(subdir="addons")
        addon = os.path.join(addon_dirs[-1], addon)
        if os.path.isdir(addon):
            time.sleep(0.1)  # give some time for the disable to take effect
            shutil.rmtree(addon)
        else:
            os.remove(addon)

class SetupAddon:
    def __init__(self, addon):
        self.addon = addon
        self.addon_dir = "local_addon"
        self.zdel_dir = []
        self.infile = None
        
        self.lwozfile = None
        self.lwozpath = None
        self.lwozfiles = None

    def configure(self, config):
        (self.bpy_module, self.zfile) = zip_addon(self.addon)
        #copy_addon(self.bpy_module, self.zfile)
        change_addon_dir(self.bpy_module, self.zfile, self.addon_dir)
        config.cache.set("bpy_module", self.bpy_module)

    def unconfigure(self):
        cleanup(self.addon, self.bpy_module)
        for z in self.zdel_dir: 
            print("Clean up zip file for {}".format(z))
            shutil.rmtree(z)

    def set_cycles(self):
        bpy.context.scene.render.engine = 'CYCLES'


def get_version(bpy_module):
    mod = sys.modules[bpy_module]
    return mod.bl_info.get("version", (-1, -1, -1))
