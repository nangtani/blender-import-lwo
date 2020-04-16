from addon_helper import SetupAddon
from lwo_helper import ImportFile
import bpy


def convert_file(infile, addon):
    x = SetupAddon(addon)
    x.configure()

    importfile = ImportFile(infile)
    importfile.check_file()
    importfile.import_object()
    importfile.save_blend()


#    x.unconfigure()


def main(infile):
    addon = "io_scene_lwo"

    # delete_everything()
    if (2, 80, 0) < bpy.app.version:
        bpy.context.scene.render.engine = "CYCLES"
    convert_file(infile, addon)


if __name__ == "__main__":
    infile = "tests/basic/src/LWO2/box/box3-uv-layers.lwo"
    # infile = "tests/src_lwo/LWO2/ISS models 2011/Objects/Modules/columbus/columbus.lwo"
    main(infile)
