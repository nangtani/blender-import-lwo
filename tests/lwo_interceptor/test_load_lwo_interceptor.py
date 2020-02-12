import pytest
from lwo_helper import load_lwo

def test_load_lwo0():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    load_lwo(infile, search_paths=["../images",])

def test_load_lwo1():
    infiles = [
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo",
    ]
    load_lwo(infiles, "_b", search_paths=["../images",])

def test_load_lwo2():
    infiles = [
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo",
    ]
    load_lwo(infiles, "_c", search_paths=["../images",], USE_EXISTING_MATERIALS=True)

def test_load_lwo3():
    infiles = [
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_R.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_reg_hull.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_reg_nacell_L.lwo",
        "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_reg_nacell_R.lwo",
    ]
    load_lwo(infiles, "_d", search_paths=["../images",], USE_EXISTING_MATERIALS=True)

def test_load_lwo4():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo"
    with pytest.raises(Exception):
        load_lwo(infile)

def test_load_lwo5():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo"
    with pytest.raises(Exception):
        load_lwo(infile, search_paths=[])

def test_load_lwo6():
    infile = "tests/lwo_interceptor/src/LWO2/Federation - Interceptor/objects/interceptor_nacell_L.lwo"
    load_lwo(infile, cancel_search=True)

