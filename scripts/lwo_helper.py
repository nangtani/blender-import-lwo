import os
import re
import shutil
import bpy
import zipfile
#from zipfile import ZipFile
from blend_helper import delete_everything, diff_files


class ImportFile:
    def __init__(self, infiles, post_pend="", delimit="/src/", *args, **kwargs):
        if isinstance(infiles, str):
            self.infiles = [infiles]
        else:
            self.infiles = infiles
        self.post_pend = post_pend
        self.zdel_dir = []
        self.search_paths = []
        self.args = args
        self.kwargs = kwargs


        self.lw_args = ()
        self.lw_kwargs = {}

        self.kwlist = [
            "ADD_SUBD_MOD",
            "LOAD_HIDDEN",
            "SKEL_TO_ARM",
            "USE_EXISTING_MATERIALS",
        ]
        for k in self.kwlist:
            if k in self.kwargs.keys():
                self.lw_kwargs[k] = self.kwargs[k]

        if "search_paths" in self.kwargs.keys():
            self.search_paths.extend(self.kwargs["search_paths"])
        else:
            pass
        #             self.search_paths.extend([
        #                 "images",
        #                 "..",
        #                 "../images",
        # #                "../../../Textures",
        #             ])
        if "cancel_search" in self.kwargs.keys():
            self.cancel_search = kwargs["cancel_search"]
        else:
            self.cancel_search = False
        if "recursive" in self.kwargs.keys():
            self.recursive = kwargs["recursive"]
        else:
            self.recursive = True

        self.infile = self.infiles[0]
        self.check_blend = False
        if re.search(delimit, self.infile):
            head, name = self.infile.split(delimit)
            dst_path = f"{head}/dst_blend/{bpy.app.version[0]}.{bpy.app.version[1]}"
            self.check_blend = True
            render = bpy.context.scene.render.engine.lower()
            self.cwd = os.getcwd()
            self.outfile = f"{dst_path}/{render}/{name}{post_pend}.blend"
            self.zipdir, self.blendfile = os.path.split(self.reffile)
            self.zipblend = f"{self.blendfile}.zip"
            self.zippath = os.path.join(self.zipdir, self.zipblend)
        else:
            name = os.path.basename(self.infile)


    @property
    def reffile(self):
        return re.sub("dst_blend", "ref_blend", self.outfile)

    def check_file(self):
        for infile in self.infiles:
            x = []
            if not os.path.exists(infile):
                elem = infile.split("/")
                for i in range(len(elem)):
                    self.zpath = "/".join(elem[0:i])
                    self.zfile = "/".join(elem[0 : i + 1]) + ".zip"
                    x.append(self.zfile)
                    if os.path.exists(self.zfile):
                        print(f"ZIP file found {self.zfile}")
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

            if not os.path.exists(infile):
                raise Exception(f"Infile or zip file not found {infile} {x}")

        if self.check_blend:
            if os.path.isfile(self.outfile):
                os.remove(self.outfile)
    
            if not os.path.exists(os.path.split(self.outfile)[0]):
                os.makedirs(os.path.split(self.outfile)[0])
            if not os.path.exists(os.path.split(self.reffile)[0]):
                os.makedirs(os.path.split(self.reffile)[0])

    def diff_result(self):
        #self.zippath = os.path.join(self.zipdir, self.zipblend)
        os.chdir(self.zipdir)
        zfiles = []
        if os.path.isfile(self.zipblend):
            zf = zipfile.ZipFile(self.zipblend, "r")
            zf.extractall()
            zfiles = zf.namelist()
            zf.close()
        
        os.chdir(self.cwd)
        
        try:
           diff_files(self.reffile, self.outfile)
        finally:
            for z in zfiles:
                zfile = os.path.join(self.zipdir, z)
                os.unlink(zfile)

    def copt_dst2ref(self, force=False, zip=True):
        #self.zippath = os.path.join(self.zipdir, self.zipblend)
        if os.path.exists(self.zippath) and not force:
            return
                 
        if not os.path.exists(self.reffile) or force:
            shutil.copyfile(self.outfile, self.reffile)

        if zip and (not os.path.exists(self.zipblend) or force):
            os.chdir(self.zipdir)
        
            with zipfile.ZipFile(self.zipblend, 'w', zipfile.ZIP_DEFLATED) as z:
                z.write(self.blendfile)
            z.close()
            if os.path.getsize(self.zipblend) >= 50*1024*1024:
                raise Exception(f"Zipfile too big: {os.path.getsize(self.zipblend)}")
            os.chdir(self.cwd)
            #os.unlink(self.reffile)
        

    def clean_up(self):
        delete_everything()
        for z in self.zdel_dir:
            print(f"Clean up zip file for {z}")
            shutil.rmtree(z)

    def import_objects(self):
        for infile in self.infiles:
            ch = bpy.types.Scene.ch
            ch.search_paths.extend(self.search_paths)
            ch.cancel_search = self.cancel_search
            ch.recursive = self.recursive
            bpy.ops.import_scene.lwo(
                filepath=infile, *self.lw_args, **self.lw_kwargs,
            )

    def save_blend(self):
        bpy.ops.wm.save_mainfile(filepath=self.outfile)


def load_lwo(infiles, post_pend="", *args, **kwargs):
    # renderers = ['CYCLES', 'BLENDER_EEVEE']
    renderers = ["CYCLES"]

    for render in renderers:
        delete_everything()
        bpy.context.scene.render.engine = render

        importfile = ImportFile(infiles, post_pend, *args, **kwargs)
        importfile.check_file()
        importfile.import_objects()
        if importfile.check_blend:
            importfile.save_blend()
            importfile.copt_dst2ref()
            importfile.diff_result()
        importfile.clean_up()

        del importfile
        bpy.types.Scene.ch.search_paths = []
        bpy.types.Scene.ch.cancel_search = False
        bpy.types.Scene.ch.recursive = True
