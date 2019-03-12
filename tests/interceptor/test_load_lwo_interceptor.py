from lwo_helper import setup_lwo, diff_files, delete_everything, load_lwo

def test_load_lwo0():
    infile = "tests/interceptor/src_lwo/LWO2/Federation - Interceptor/objects/interceptor_hull.lwo"
    load_lwo(infile)
