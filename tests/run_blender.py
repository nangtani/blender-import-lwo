import os
import sys
import re


def checkPath(path):
    path = os.path.realpath(path)
    if re.match("/cygdrive/", path):
        path = re.sub("/cygdrive/", "", path)
        path = re.sub("/", "\\\\", path)
        path = (path[:1] + ":" + path[1:]).capitalize()

    return path


def main(blender, test_file, background="--background"):
    test_file = checkPath(test_file)
    os.environ["PYTHONPATH"] = os.getcwd() + "/tests"
    os.environ["PYTHONPATH"] = checkPath(os.environ["PYTHONPATH"])

    cmd = f'{blender} {background} --python "{test_file}"'
    result = int(os.system(cmd))
    if 0 == result:
        return 0
    else:
        return 1


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        blender_rev = sys.argv[1]
    else:
        blender_rev = "2.79b"
    
    blender_dir = "blender_build/blender-{0}".format(blender_rev)

    blender = os.path.realpath("{0}/blender".format(blender_dir))

    test_file = "tests/load_pytest.py"

    exit_val = main(blender, test_file)

    sys.exit(exit_val)
