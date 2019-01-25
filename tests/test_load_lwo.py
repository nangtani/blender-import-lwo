import pytest
import bpy
from lwo_helper import setup_lwo, diff_files


def test_load_lwo_box1():
    infile = "tests/src_lwo/box/box1.lwo"
    outfile0, outfile1 = setup_lwo(infile)

    bpy.ops.import_scene.lwo(filepath=infile)
    bpy.ops.wm.save_mainfile(filepath=outfile0)

    diff_files(outfile1, outfile0)


# def test_load_lwo_box1_uv():
#     infile = 'tests/src_lwo/box/box1-uv.lwo'
#     outfile0, outfile1 = setup_lwo(infile)
#
#     bpy.ops.import_scene.lwo(filepath=infile)
#     bpy.ops.wm.save_mainfile(filepath=outfile0)
#
#     diff_files(outfile1, outfile0)
