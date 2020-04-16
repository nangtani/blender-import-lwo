import os
import sys

sys.path.append(os.environ["LOCAL_PYTHONPATH"])
from addon_helper import SetupAddon
from lwo_helper import ImportFile
import bpy


def convert_file(infiles, addon):
    x = SetupAddon(addon)
    x.configure()

    #importfile = ImportFile(infiles, search_paths=["../../../Images/Star Trek/Archer Class", ])
    importfile = ImportFile(infiles, search_paths=["../images", ])
    importfile.check_file()
    importfile.import_objects()

    importfile.save_blend()
    importfile.copt_dst2ref()
    importfile.diff_result()
    importfile.clean_up()

    x.unconfigure()


def main(infiles):
    addon = "io_scene_lwo"

    if (2, 80, 0) < bpy.app.version:
        bpy.context.scene.render.engine = "CYCLES"
    convert_file(infiles, addon)


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
        # "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo",
    ]
    # infiles = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo"    #infile = "tests/basic/src/LWO2/box/box3-uv-layers.lwo"
    # infile = "tests/basic/src/LWO3/box/box3-uv-layers.lwo"
    # infile = "tests/basic/src/LWO2/ISS models 2011/Objects/Modules/columbus/columbus.lwo"
    infiles = "tests/lwo_phobos/src/LWO2/Federation - Phobos/objects/USS-Phobos.lwo"
    infiles = "tests/lwo_nasa/src/ATLAST/ATLAST-2014.lwo"
    infiles = "tests/lwo_nasa/src/GeoTailSAT/GeoTailSAT.lwo"
    infiles = "tests/lwo_nasa/src/Wide Field Infrared Survey Telescope (WFIRST)/WFirst-2015-composite.lwo"
    infiles = "tests/lwo_nasa/src/STEREO/Stereo-2016-comp.lwo"
    infiles = 'tests/lwo_bulk/src/ST2_Bridge/st2 bridge2.lwo',
    infiles = 'tests/lwo_bulk/src/Federation - Enterprise/newtek/objects/1701_STTMP/lightwave/enterprise_st_tmp_engineering_hull_and_pylons.lwo',
    #infiles = "tests/lwo_nasa/src/Gamma Ray Observatory - Composite/GRO-Composite.lwo"
    #infiles = 'tests/lwo_bulk/src/Archer_Class_1_1/Objects/Star Trek/Archer Class/Archer Main.lwo'
    main(infiles)
