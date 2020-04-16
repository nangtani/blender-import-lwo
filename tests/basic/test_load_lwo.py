import pytest
import os
import sys
sys.path.append(os.environ["ADDON_TEST_HELPER"])
raise Exception(sys.path, os.environ["ADDON_TEST_HELPER"])
from lwo_helper import load_lwo

def test_load_lwo_box1():
    infile = "tests/basic/src/LWO2/box/box1.lwo"
    load_lwo(infile)


def test_load_lwo_box1_uv():
    infile = "tests/basic/src/LWO2/box/box1-uv.lwo"
    load_lwo(infile)


def test_load_lwo_box2_uv():
    infile = "tests/basic/src/LWO2/box/box2-uv.lwo"
    load_lwo(infile)


def test_load_lwo5_box3_uv_layers():
    infile = "tests/basic/src/LWO/box/box3-uv-layers.lwo"
    load_lwo(infile)


def test_load_lwo_box3_uv_layers():
    infile = "tests/basic/src/LWO2/box/box3-uv-layers.lwo"
    load_lwo(infile)


def test_load_lwo_box5_ngon():
    infile = "tests/basic/src/LWO2/box/box5-ngon.lwo"
    load_lwo(infile)


def test_load_lwo_ngon0():
    infile = "tests/basic/src/LWO2/ngon/ngon0.lwo"
    load_lwo(infile)


def test_load_lwo_raise0():
    infile = "tests/basic/src/LWO2/box/cc0.png"
    with pytest.raises(Exception):
        load_lwo(infile)


def test_load_lwo_raise1():
    infile = "tests/basic/src/LWO2/box/cc0.pdf"
    with pytest.raises(Exception):
        load_lwo(infile)

def test_load_lwo_basic_name():
    infile = "tests/basic/src/LWO2/naming/box0.lwo"
    load_lwo(infile, search_paths=["../images"],)

def test_load_lwo_advance_name():
    infile = "tests/basic/src/LWO2/naming/box1.lwo"
    load_lwo(infile, search_paths=["../images"],)

