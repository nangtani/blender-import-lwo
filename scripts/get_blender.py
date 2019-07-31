import os
import sys
import shutil
import subprocess
import zipfile
import tarfile
import requests
import re
from glob import glob
from bs4 import BeautifulSoup


def checkPath(path):
    if "cygwin" == sys.platform:
        cmd = "cygpath -wa {0}".format(path)
        path = subprocess.check_output(cmd.split()).decode("ascii").rstrip()
    return path


def getSuffix(blender_version, nightly):
    if "win32" == sys.platform or "win64" == sys.platform or "cygwin" == sys.platform:
        machine = "win64"
        ext = "zip"
    else:
        machine = "linux.+x86_64"
        ext = "tar.bz2"

    g = re.search(f"\d\.\d\d", blender_version)
    if g:
        rev = g.group(0)
    else:
        raise
        
    if False == nightly:
        url = f"https://ftp.nluug.nl/pub/graphics/blender/release/Blender{rev}"
        if "win64" == machine:
            machine = "windows64"
    else:
        url = "https://builder.blender.org/download"

    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")

    blender_version_suffix = ""
    blender_zippath = None
    versions_found = []
    for link in soup.find_all("a"):
        x = str(link.get("href"))
        g = re.search(f"blender-(.+)-{machine}.+{ext}", x)
        if g:
            version_found = g.group(1).split("-")[0]
            versions_found.append(version_found)
            if version_found == blender_version:
                blender_zippath = f"{url}/{g.group(0)}"

    if None == blender_zippath:
        raise Exception(f"Unable to find {blender_version} in nightlies, here is what is available {versions_found}")
    return blender_zippath


def getBlender(blender_version, blender_zippath, nightly):
    cwd = checkPath(os.getcwd())
    if "BLENDER_CACHE" in os.environ.keys():
        print(f"BLENDER_CACHE found {os.environ['BLENDER_CACHE']}")
        os.chdir(os.environ["BLENDER_CACHE"])
    else:
        os.chdir("..")
    cache_dir = checkPath(os.getcwd())

    blender_zipfile = blender_zippath.split("/")[-1]

    files = glob(blender_zipfile)

    if 0 == len(files):
        if not os.path.exists(blender_zipfile):
            r = requests.get(blender_zippath, stream=True)
            print(f"Downloading {blender_zippath}")
            open(blender_zipfile, "wb").write(r.content)

    if blender_zipfile.endswith("zip"):
        z = zipfile.ZipFile(blender_zipfile, "r")
        zfiles = z.namelist()
    else:
        z = tarfile.open(blender_zipfile)
        zfiles = z.getnames()

    zdir = zfiles[0].split("/")[0]
    if not os.path.isdir(zdir):
        print(f"Unpacking {blender_zipfile}")
        z.extractall()
    z.close()
    blender_archive = zdir

    for zfile in zfiles:
        if re.search("bin/python.exe", zfile) or re.search("bin/python\d.\d", zfile):
            python = os.path.realpath(zfile)

    cmd = f"{python} -m ensurepip"
    os.system(cmd)
    cmd = f"{python} -m pip install --upgrade -r {cwd}/blender_requirements.txt -r {cwd}/scripts/requirements.txt"
    os.system(cmd)

    os.chdir(cwd)

    shutil.rmtree("tests/__pycache__", ignore_errors=True)

    ext = ""
    if nightly == True:
        ext = "-nightly"
    dst = f"../blender-{blender_version}{ext}"

    if os.path.exists(dst):
        shutil.rmtree(dst)

    src = f"{cache_dir}/{blender_archive}"
    print(f"move {src} to {dst}")
    shutil.move(src, dst)


def main(blender_version, nightly=True):

    blender_zipfile = getSuffix(blender_version, nightly)

    getBlender(blender_version, blender_zipfile, nightly)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        blender_rev = sys.argv[1]
    else:
        blender_rev = "2.79b"

    if re.search("-", blender_rev):
        blender_rev, _ = blender_rev.split("-")
        nightly = True
    else:
        nightly = False

    main(blender_rev, nightly)
