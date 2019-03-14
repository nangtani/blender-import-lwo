import os
import re
import zipfile
import shutil
import bpy
from blend_helper import delete_everything, diff_files

class ImportFile(object):
    
    def __init__(self, infile, delimit="/src/"):
        self.infile = infile
        self.zdel_dir = []

        if re.search(delimit, infile):
            head, name = infile.split(delimit)
        else:
            name = os.path.basename(infile)
    
        render = bpy.context.scene.render.engine.lower()
        dst_path = "{0}/dst_blend/{1}.{2}".format(head, bpy.app.version[0],bpy.app.version[1])
        self.outfile = "{0}/{1}/{2}.blend".format(dst_path, render, name)
    
    @property
    def reffile(self):
        return re.sub("dst_blend", "ref_blend", self.outfile)
    
    def check_file(self):
        edit_infile = self.infile
        #edit_infile = re.sub("\\\\", "/", edit_infile)
        if not os.path.exists(self.infile):
            elem = edit_infile.split("/")
            for i in range(len(elem)):
                self.zpath = "/".join(elem[0:i])
                self.zfile = "/".join(elem[0:i+1]) + ".zip"
                if os.path.exists(self.zfile):
                    print("ZIP file found {}".format(self.zfile))
                    break
                self.zfile = None
            
            if not None == self.zfile:
                zf = zipfile.ZipFile(self.zfile, "r")
                zf.extractall(self.zpath)
                self.zfiles = zf.namelist()
                zf.close()
                zdir = os.path.join(self.zpath, self.zfiles[0].split("/")[0])
                if not os.path.isdir(zdir):
                    raise Exception(zdir)
                self.zdel_dir.append(zdir)

        if os.path.isfile(self.outfile):
            os.remove(self.outfile)

        if not os.path.exists(os.path.split(self.outfile)[0]):
            os.makedirs(os.path.split(self.outfile)[0])
        if not os.path.exists(os.path.split(self.reffile)[0]):
            os.makedirs(os.path.split(self.reffile)[0])
    
    def diff_result(self):
        diff_files(self.reffile, self.outfile)
    
    def clean_up(self):
        delete_everything()
        for z in self.zdel_dir: 
            print("Clean up zip file for {}".format(z))
            shutil.rmtree(z)
    
    def import_object(self):
        delete_everything()
        bpy.ops.import_scene.lwo(filepath=self.infile)

    def save_blend(self):
        bpy.ops.wm.save_mainfile(filepath=self.outfile)


def load_lwo(infile):
    if (2, 80, 0) < bpy.app.version:
        renderers = ['CYCLES']
    elif (2, 79, 0) < bpy.app.version:
        renderers = ['BLENDER_RENDER', 'CYCLES']
    else:
        renderers = ['BLENDER_RENDER']
    
    for render in renderers:
        bpy.context.scene.render.engine = render
        
        importfile = ImportFile(infile)
        importfile.check_file()
        importfile.import_object()
        importfile.save_blend()
        importfile.diff_result()
        importfile.clean_up()

