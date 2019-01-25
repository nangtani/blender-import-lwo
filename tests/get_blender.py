import os
import sys
import shutil
import zipfile
import tarfile
import requests
import re
from glob import glob
from bs4 import BeautifulSoup


def checkPath(path):
    path = os.path.realpath(path)
    if re.match("/cygdrive/", path):
        path = re.sub("/cygdrive/", "", path)
        path = re.sub("/", "\\\\", path)
        path = (path[:1] + ":" + path[1:]).capitalize()

    return path


def getSuffix(blender_version):
    url = "https://builder.blender.org/download"

    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")

    blender_version_suffix = ""
    # print(sys.platform)
    if "win32" == sys.platform or "win64" == sys.platform or "cygwin" == sys.platform:
        machine = "win64"
    else:
        machine = "linux.+x86_64"
    # machine = "linux.+x86_64"
    for link in soup.find_all("a"):
        x = str(link.get("href"))
        # of the format blender-2.79-e6acb4fba094-linux-glibc224-x86_64.tar.bz2
        g = re.search("blender-{0}-(\w+)-{1}.+".format(blender_version, machine), x)
        if g:
            blender_zipfile = g.group(0)
            blender_version_suffix = g.group(1)
    return (blender_version_suffix, blender_zipfile)


def getBlender(blender_version, blender_version_suffix, blender_zipfile):
    cwd = checkPath(os.getcwd())
    os.chdir("..")

    if re.search("linux", blender_zipfile):
        machine = "linux"
        s = "blender*{0}*{1}*x86_64".format(blender_version, blender_version_suffix)
    else:
        machine = "windows"
        s = "blender*{0}*{1}*windows64".format(blender_version, blender_version_suffix)
    # print(blender_zipfile)
    files = glob(s)
    if 0 == len(files):
        if not os.path.exists(blender_zipfile):
            url = "https://builder.blender.org/download/{0}".format(blender_zipfile)
            r = requests.get(url, stream=True)
            print("Downloading {0}".format(url))
            open(blender_zipfile, "wb").write(r.content)

        print("Unpacking {0}".format(blender_zipfile))
        if blender_zipfile.endswith("zip"):
            z = zipfile.ZipFile(blender_zipfile, "r")
            z.extractall()
            z.close()
            # cmd = "unzip {0}".format(blender_zipfile)
        else:
            z = tarfile.open(blender_zipfile)
            z.extractall()
            z.close()
        # os.remove(blender_zipfile)

    files = glob(s)
    blender_archive = files[0]

    if "linux" == machine:
        python = os.path.realpath(
            "{0}/{1}/python/bin/python3.7m".format(blender_archive, blender_version)
        )
    else:
        python = os.path.realpath(
            "{0}/{1}/python/bin/python".format(blender_archive, blender_version)
        )
    cmd = "{0} -m ensurepip".format(python)
    os.system(cmd)
    cmd = "{0} -m pip install --upgrade -r {1}/blender_requirements.txt -r {1}/tests/requirements.txt".format(
        python, cwd
    )
    # print(cmd)
    os.system(cmd)

    os.chdir(cwd)

    shutil.rmtree("tests/__pycache__", ignore_errors=True)

    blender_dir = "blender_build"
    if not os.path.exists(blender_dir):
        os.mkdir(blender_dir)

    os.chdir(blender_dir)
    link_path = "blender-{0}".format(blender_version)

    if os.path.exists(link_path):
        os.remove(link_path)

    try:
        os.symlink("../../{0}".format(blender_archive), link_path)
    except OSError:  # Windows can't add links
        pass


def main(blender_version, download=False):

    (blender_version_suffix, blender_zipfile) = getSuffix(blender_version)
    print("-" + blender_version_suffix)

    if download:
        getBlender(blender_version, blender_version_suffix, blender_zipfile)


if __name__ == "__main__":
    download = False
    if len(sys.argv) >= 3:
        download = True

    if len(sys.argv) >= 2:
        blender_rev = sys.argv[1]
    else:
        blender_rev = "2.79"
    main(blender_rev, download)
