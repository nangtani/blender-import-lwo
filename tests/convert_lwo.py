from addon_helper import SetupAddon


def convert_file(infile, addon):
    x = SetupAddon(addon)
    x.configure()

    x.convert_lwo(infile)

    x.unconfigure()


def main(infile):
    # addon = "io_import_scene_lwo.py"
    addon = "io_import_scene_lwo"

    convert_file(infile, addon)


if __name__ == "__main__":
    infile = "tests/src_lwo/box/box1.lwo"
    infile = "tests/src_lwo/box/box1-uv.lwo"
    #infile = "src_lwo/Federation - Phobos/objects/USS-Phobos.lwo"
    #infile = "src_lwo/Federation - Phobos/objects/USS-Phobos.11.5.lwo"
    infile = "src_lwo/Federation - Interceptor/objects/interceptor_hull.lwo"
    main(infile)
