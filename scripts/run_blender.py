import os
import sys
import subprocess
import re


def checkPath(path):
    if "cygwin" == sys.platform:
        cmd = "cygpath -wa {0}".format(path)
        path = subprocess.check_output(cmd.split()).decode('ascii').rstrip()
    return path

def main(blender, test_file):
    test_file = checkPath(test_file)
    os.environ["PYTHONPATH"] = os.getcwd() + "/scripts"
    os.environ["PYTHONPATH"] = checkPath(os.environ["PYTHONPATH"])

    cmd = '{0} --background --python "{1}"'.format(blender, test_file)
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
    
    blender_dir = "../blender-{0}".format(blender_rev)

    blender = os.path.realpath("{0}/blender".format(blender_dir))

    test_file = "scripts/load_pytest.py"

    exit_val = main(blender, test_file)

    sys.exit(exit_val)
