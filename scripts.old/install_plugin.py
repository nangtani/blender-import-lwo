import os
import sys

sys.path.append(os.environ["LOCAL_PYTHONPATH"])
from addon_helper import SetupAddon
from lwo_helper import ImportFile
import bpy


def install_plugin(addon):
    x = SetupAddon(addon)
    x.configure()
    # rev = "2.79b"
    blender = os.environ["LOCAL_BLENDER"]
    # cmd = "..\\blender-{}-nightly\\blender.exe".format(rev)
    print(blender)
    os.system(blender)
    x.unconfigure()


def main(infiles):
    addon = "io_scene_lwo"

    if (2, 80, 0) < bpy.app.version:
        bpy.context.scene.render.engine = "CYCLES"
    install_plugin(addon)


if __name__ == "__main__":
    infiles = "tests/basic/src/box/box1.lwo"
    # infile = "tests/basic/src/box/box1-uv.lwo"
    # infile = "tests/basic/src/LWO2/box/box2-uv.lwo"
    # infile = "tests/basic/src/LWO2/box/box3-uv-layers.lwo"
    # infile = "tests/basic/src/LWO/box/box3-uv-layers.lwo"
    # infile = "tests/basic/src/LWO2/box/box4-uv-layers.lwo"
    infiles = "tests/basic/src/LWO2/box/box5-ngon.lwo"
    infiles = ["tests/basic/src/LWO2/ngon/ngon3.lwo"]
    # infile = "tests/basic/src/LWO2/ngon/ngon0.lwo"
    # infile = "tests/basic/src/LWO2/src/Federation - Phobos/objects/USS-Phobos.lwo"
    # infile = "tests/lwo_phobos/src/LWO2/Federation - Phobos/objects/USS-Phobos.lwo"
    # infile = "src/Federation - Phobos/objects/USS-Phobos.11.5.lwo"
    infiles = [
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo",
    ]
    infile = "tests/basic/src/LWO2/box/box3-uv-layers.lwo"
    # infile = "tests/basic/src/LWO3/box/box3-uv-layers.lwo"
    # infile = "tests/basic/src/LWO2/ISS models 2011/Objects/Modules/columbus/columbus.lwo"
    # infile = "tests/lwo_phobos/src/LWO2/Federation - Phobos/objects/USS-Phobos.lwo"
    main(infiles)
