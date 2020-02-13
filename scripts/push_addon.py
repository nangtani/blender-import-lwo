import os
import sys
import subprocess


def checkPath(path):
    if "cygwin" == sys.platform:
        cmd = "cygpath -wa {0}".format(path)
        path = subprocess.check_output(cmd.split()).decode("ascii").rstrip()
    return path


def main(blender, test_file, background="--background"):
    test_file = checkPath(test_file)
    os.environ["PYTHONPATH"] = os.getcwd() + "/scripts"
    os.environ["PYTHONPATH"] = checkPath(os.environ["PYTHONPATH"])

    cmd = "rm -rf ../blender-*/*/scripts/addons/io_import_scene_lwo.py"
    os.system(cmd)

    cmd = f'{blender} {background} --python "{test_file}"'
    result = int(os.system(cmd))
    if 0 == result:
        return 0
    else:
        return 1


if __name__ == "__main__":

    infile = "tests/load_pytest.py"
    if len(sys.argv) >= 3:
        infile = sys.argv[2]

    try:
        blender_rev = sys.argv[1]
    except:
        blender_rev = "2.79"

    blender_dir = "../blender-{0}".format(blender_rev)

    blender = os.path.realpath("{0}/blender".format(blender_dir))

    exit_val = main(blender, infile, "")

    sys.exit(exit_val)
