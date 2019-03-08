from addon_helper import SetupAddon
from lwo_helper import delete_everything
import bpy


def convert_file(infile, addon):
    x = SetupAddon(addon)
    x.configure()
    
#     #x.set_cycles()
# 
    x.convert_lwo(infile)
# 
#    x.unconfigure()


def main(infile):
    addon = "io_import_scene_lwo"

    delete_everything()
    if (2, 80, 0) < bpy.app.version:
        bpy.context.scene.render.engine = 'CYCLES'
    convert_file(infile, addon)


if __name__ == "__main__":
    infile = "tests/src_lwo/LWO2/box/box3-uv-layers.lwo"
    #infile = "tests/src_lwo/LWO2/ISS models 2011/Objects/Modules/columbus/columbus.lwo"
    main(infile)
