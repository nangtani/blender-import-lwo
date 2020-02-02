import os
import sys
sys.path.append(os.environ["LOCAL_PYTHONPATH"])
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
    importfile.clean_up()

    x.unconfigure()


def main(infile):
    # addon = "io_import_scene_lwo.py"
    # addon = "io_import_scene_lwo_1_3b.py"
    addon = "io_import_scene_lwo"

    if (2, 80, 0) < bpy.app.version:
        bpy.context.scene.render.engine = 'CYCLES'
    convert_file(infile, addon)


if __name__ == "__main__":
    infile = "tests/basic/src/box/box1.lwo"
    #infile = "tests/basic/src/box/box1-uv.lwo"
    #infile = "tests/basic/src/LWO2/box/box2-uv.lwo"
    #infile = "tests/basic/src/LWO2/box/box3-uv-layers.lwo"
    #infile = "tests/basic/src/LWO/box/box3-uv-layers.lwo"
    #infile = "tests/basic/src/LWO2/box/box4-uv-layers.lwo"
    #infile = "tests/basic/src/LWO2/box/box5-ngon.lwo"
    #infile = "tests/basic/src/LWO2/src/Federation - Phobos/objects/USS-Phobos.lwo"
    #infile = "tests/lwo_phobos/src/LWO2/Federation - Phobos/objects/USS-Phobos.lwo"
    #infile = "src/Federation - Phobos/objects/USS-Phobos.11.5.lwo"
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    #infile = "tests/basic/src/LWO2/box/box3-uv-layers.lwo"
    #infile = "tests/basic/src/LWO3/box/box3-uv-layers.lwo"
    #infile = "tests/basic/src/LWO2/ISS models 2011/Objects/Modules/columbus/columbus.lwo"
    #infile = "tests/lwo_phobos/src/LWO2/Federation - Phobos/objects/USS-Phobos.lwo"
    main(infile)
