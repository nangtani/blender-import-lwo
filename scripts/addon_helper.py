import os
import sys
import re
import time
import zipfile
import shutil
import bpy

def mkdir_p(outfile):
    outfile = re.sub("\\\\", "/", outfile)
    dirname = os.path.dirname(outfile).split("/")
    for i in range(len(dirname)):
        new_path = "/".join(dirname[0:i+1])
        if not os.path.isdir(new_path):
            os.mkdir(new_path)

def zip_addon(addon):
    bpy_module = re.sub(".py", "", os.path.basename(os.path.realpath(addon)))
    zfile = os.path.realpath(bpy_module + ".zip")

    print(f"Zipping addon - {bpy_module}")

    zf = zipfile.ZipFile(zfile, "w")
    if os.path.isdir(addon):
        for dirname, subdirs, files in os.walk(addon):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
    else:
        zf.write(addon)
    zf.close()
    return (bpy_module, zfile)


def copy_addon(bpy_module, zfile):
    print(f"Copying addon - {bpy_module} {zfile}")

    if (2, 80, 0) < bpy.app.version:
        bpy.ops.preferences.addon_install(overwrite=True, filepath=zfile)
        bpy.ops.preferences.addon_enable(module=bpy_module)
    else:
        bpy.ops.wm.addon_install(overwrite=True, filepath=zfile)
        bpy.ops.wm.addon_enable(module=bpy_module)


def cleanup(addon, bpy_module):
    print(f"Cleaning up - {bpy_module}")
    if (2, 80, 0) < bpy.app.version:
        bpy.ops.preferences.addon_disable(module=bpy_module)
        bpy.ops.preferences.addon_remove(bpy_module=bpy_module)
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

class SetupAddon(object):
    def __init__(self, addon):
        self.addon = addon
        self.zdel_dir = []
        self.infile = None
        
        self.lwozfile = None
        self.lwozpath = None
        self.lwozfiles = None

    def configure(self):
        (self.bpy_module, self.zfile) = zip_addon(self.addon)
        copy_addon(self.bpy_module, self.zfile)

    def unconfigure(self):
        cleanup(self.addon, self.bpy_module)
        for z in self.zdel_dir: 
            print(f"Clean up zip file for {z}")
            shutil.rmtree(z)

    def convert_lwo(self, infile, outfile=None):
        self.infile = infile
        self.infile = re.sub("\\\\", "/", self.infile)
        if not os.path.exists(infile):
            elem = self.infile.split("/")
            for i in range(len(elem)):
                self.lwozpath = "/".join(elem[0:i])
                self.lwozfile = "/".join(elem[0:i+1]) + ".zip"
                if os.path.exists(self.lwozfile):
                    print(f"ZIP file found {self.lwozfile}")
                    break
            
            if not None == self.lwozfile:
                zf = zipfile.ZipFile(self.lwozfile, "r")
                zf.extractall(self.lwozpath)
                self.lwozfiles = zf.namelist()
                zf.close()
                zdir = os.path.join(self.lwozpath, self.lwozfiles[0].split("/")[0])
                if not os.path.isdir(zdir):
                    raise
                self.zdel_dir.append(zdir)
                print(self.zdel_dir)
        
        bpy.ops.import_scene.lwo(filepath=self.infile)
        
        if None == outfile:
            rev = f"{bpy.app.version[0]}.{bpy.app.version[1]}"
            new_path = f"ref_blend/{rev}/{bpy.context.scene.render.engine.lower()}"
            outfile = re.sub("src_lwo", new_path, self.infile + ".blend")
        
        mkdir_p(outfile)
                
        bpy.ops.wm.save_mainfile(filepath=outfile)

    def set_cycles(self):
        bpy.context.scene.render.engine = 'CYCLES'


def get_version(bpy_module):
    mod = sys.modules[bpy_module]
    return mod.bl_info.get("version", (-1, -1, -1))
