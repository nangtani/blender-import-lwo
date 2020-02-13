import os
import re
import zipfile
import shutil
import bpy
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

        self.infile = self.infiles[0]
        if re.search(delimit, self.infile):
            head, name = self.infile.split(delimit)
        else:
            name = os.path.basename(self.infile)

        render = bpy.context.scene.render.engine.lower()
        dst_path = "{0}/dst_blend/{1}.{2}".format(
            head, bpy.app.version[0], bpy.app.version[1]
        )
        self.outfile = "{0}/{1}/{2}{3}.blend".format(dst_path, render, name, post_pend)

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

            if not os.path.exists(infile):
                raise Exception("Infile or zip file not found {} {}".format(infile, x))

        if os.path.isfile(self.outfile):
            os.remove(self.outfile)

        if not os.path.exists(os.path.split(self.outfile)[0]):
            os.makedirs(os.path.split(self.outfile)[0])
        if not os.path.exists(os.path.split(self.reffile)[0]):
            os.makedirs(os.path.split(self.reffile)[0])

    def diff_result(self):
        diff_files(self.reffile, self.outfile)

    def copt_dst2ref(self, force=False):
        if not os.path.exists(self.reffile) or force:
            shutil.copyfile(self.outfile, self.reffile)

    def clean_up(self):
        delete_everything()
        for z in self.zdel_dir:
            print("Clean up zip file for {}".format(z))
            shutil.rmtree(z)

    def import_objects(self):
        for infile in self.infiles:
            ch = bpy.types.Scene.ch
            ch.search_paths.extend(self.search_paths)
            ch.cancel_search = self.cancel_search
            bpy.ops.import_scene.lwo(
                filepath=infile, *self.lw_args, **self.lw_kwargs,
            )

    def save_blend(self):
        bpy.ops.wm.save_mainfile(filepath=self.outfile)


def load_lwo(infiles, post_pend="", *args, **kwargs):
    if (2, 80, 0) < bpy.app.version:
        # renderers = ['CYCLES', 'BLENDER_EEVEE']
        renderers = ["CYCLES"]
    elif (2, 79, 0) < bpy.app.version:
        renderers = ["BLENDER_RENDER", "CYCLES"]
    else:
        renderers = ["BLENDER_RENDER"]

    for render in renderers:
        delete_everything()
        bpy.context.scene.render.engine = render

        importfile = ImportFile(infiles, post_pend, *args, **kwargs)
        importfile.check_file()
        importfile.import_objects()
        importfile.save_blend()
        importfile.copt_dst2ref()
        importfile.diff_result()
        importfile.clean_up()

        del importfile
        bpy.types.Scene.ch.search_paths = []
        bpy.types.Scene.ch.cancel_search = False
