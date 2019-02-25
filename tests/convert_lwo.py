from addon_helper import SetupAddon
from lwo_helper import delete_everything
import bpy


def convert_file(infile, addon):
    x = SetupAddon(addon)
    x.configure()
    
    #x.set_cycles()

    x.convert_lwo(infile)

    x.unconfigure()


def main(infile):
    # addon = "io_import_scene_lwo.py"
    # addon = "io_import_scene_lwo_1_3b.py"
    addon = "io_import_scene_lwo"

    delete_everything()
    if (2, 80, 0) < bpy.app.version:
        bpy.context.scene.render.engine = 'CYCLES'
    convert_file(infile, addon)


if __name__ == "__main__":
    #infile = "tests/src_lwo/box/box1.lwo"
    #infile = "tests/src_lwo/box/box1-uv.lwo"
    infile = "tests/src_lwo/LWO2/box/box2-uv.lwo"
    infile = "tests/src_lwo/LWO2/box/box3-uv-layers.lwo"
    infile = "tests/src_lwo/LWO/box/box3-uv-layers.lwo"
    #infile = "tests/src_lwo/LWO2/box/box4-uv-layers.lwo"
    #infile = "tests/src_lwo/LWO2/box/box5-ngon.lwo"
    #infile = "tests/src_lwo/LWO2/src_lwo/Federation - Phobos/objects/USS-Phobos.lwo"
    #infile = "tests/src_lwo/LWO2/Federation - Phobos/objects/USS-Phobos.lwo"
    #infile = "src_lwo/Federation - Phobos/objects/USS-Phobos.11.5.lwo"
    infile = "tests/src_lwo/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    #infile = "tests/src_lwo/LWO2/box/box3-uv-layers.lwo"
    #infile = "tests/src_lwo/LWO3/box/box3-uv-layers.lwo"
    #infile = "tests/src_lwo/LWO2/ISS models 2011/Objects/Modules/columbus/columbus.lwo"
    main(infile)
