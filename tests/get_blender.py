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


def getSuffix(blender_version, nightly):
    if "win32" == sys.platform or "win64" == sys.platform or "cygwin" == sys.platform:
        machine = "win64"
        ext = "zip"
    else:
        machine = "linux.+x86_64"
        ext = "tar.bz2"

    if False == nightly:
        url = "https://www.blender.org/download"
        download_url = "https://ftp.nluug.nl/pub/graphics/blender/release"
        if "win64" == machine:
            machine = "windows64"
    else:
        url = "https://builder.blender.org/download"
        download_url = url

    page = requests.get(url)
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")

    blender_version_suffix = ""
    for link in soup.find_all("a"):
        x = str(link.get("href"))
        g = re.search(f".+blender-{blender_version}.+{machine}.+{ext}", x)
        if g:
            blender_zippath = re.sub("^.+download", download_url, g.group(0))
            break

#     g = re.search(f"blender-{blender_version}-(\w+).+", blender_zippath)
#     if g:
#         blender_version_suffix = g.group(1)
    return (blender_zippath)


def getBlender(blender_version, blender_zippath, nightly):
    cwd = checkPath(os.getcwd())
    os.chdir("..")

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
    # os.remove(blender_zipfile)

    for zfile in zfiles:
        if re.search("bin/python.exe", zfile) or re.search("bin/python\d.\d", zfile):
            python = os.path.realpath(zfile)

    cmd = f"{python} -m ensurepip"
    os.system(cmd)
    cmd = f"{python} -m pip install --upgrade -r {cwd}/blender_requirements.txt -r {cwd}/tests/requirements.txt"
    os.system(cmd)

    os.chdir(cwd)

    shutil.rmtree("tests/__pycache__", ignore_errors=True)

    blender_dir = "blender_build"
    if not os.path.exists(blender_dir):
        os.mkdir(blender_dir)

    ext = ""
    if nightly == True:
        ext = "-nightly"
    os.chdir(blender_dir)
    link_path = f"blender-{blender_version}{ext}"

    if os.path.exists(link_path):
        os.remove(link_path)

    try:
        os.symlink(f"../../{blender_archive}", link_path)
    except OSError:  # Windows can't add links
        pass
    
    #cmd = f"rm -rf blender_build/*/*/scripts/addons/io_import_scene_lwo.py"
    #os.system(cmd)

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
#        
    main(blender_rev, nightly)
