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

def findVersions(rev):

    if "win32" == sys.platform or "win64" == sys.platform or "cygwin" == sys.platform:
        machine = "windows64"
        ext = "zip"
    else:
        machine = "linux.*64"
        ext = "tar.xz"

    urls = [
        f"https://ftp.nluug.nl/pub/graphics/blender/release/Blender{rev}",
        "https://builder.blender.org/download",
    ]
    nightly = False
    for url in urls:
        page = requests.get(url)
        data = page.text
        soup = BeautifulSoup(data, features="html.parser")

        blender_version_suffix = ""
        versions_found = {}
        for link in soup.find_all("a"):
            x = str(link.get("href"))
            if g:= re.search(f"blender-(.+)-{machine}.+{ext}$", x):
                version_found = g.group(1).split("-")[0]
                if not version_found in versions_found.keys():
                    versions_found[version_found] = x
    return versions_found
    
def getSuffix(blender_version):

    if g := re.search(r"\d\.\d", blender_version):
        rev = g.group(0)
    else:
        raise
    
    versions_found = findVersions(rev)

    blender_zippath = None
    for key in versions_found.keys():
        #print(rev, key)
        if g := re.search(rev, key):
            #print(versions_found[key])
            blender_zippath = versions_found[key]

    if None == blender_zippath:
        print(soup)
        raise Exception(
            f"Unable to find {blender_version} in nightlies, here is what is available {versions_found}"
        )

    # print(blender_zippath, nightly)
    # exit()
    return blender_zippath, False


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

#     if 0 == len(files):
#         if not os.path.exists(blender_zipfile):
#             r = requests.get(blender_zippath, stream=True)
#             print(f"Downloading {blender_zippath}")
#             open(blender_zipfile, "wb").write(r.content)
# 
#     if blender_zipfile.endswith("zip"):
#         z = zipfile.ZipFile(blender_zipfile, "r")
#         zfiles = z.namelist()
#     else:
#         z = tarfile.open(blender_zipfile)
#         zfiles = z.getnames()
# 
#     zdir = zfiles[0].split("/")[0]
#     if not os.path.isdir(zdir):
#         print(f"Unpacking {blender_zipfile}")
#         z.extractall()
#     z.close()
#     blender_archive = zdir
# 
#     for zfile in zfiles:
#         if re.search("bin/python.exe", zfile) or re.search(r"bin/python\d.\d", zfile):
#             python = os.path.realpath(zfile)
# 
#     if os.path.isfile(f"{cwd}/blender_requirements_{blender_version}.txt"):
#         bl_requirements = f"{cwd}/blender_requirements_{blender_version}.txt"
#     else:
#         bl_requirements = f"{cwd}/blender_requirements.txt"
#     cmd = f"{python} -m ensurepip"
#     os.system(cmd)
#     cmd = f"{python} -m pip install --upgrade -r {bl_requirements} -r {cwd}/scripts/requirements.txt"
#     print(cmd)
#     os.system(cmd)
#     cmd = f"{python} -m pip list"
#     print(cmd)
#     os.system(cmd)
# 
#     os.chdir(cwd)
# 
#     shutil.rmtree("tests/__pycache__", ignore_errors=True)
# 
#     ext = ""
#     if nightly == True:
#         ext = "-nightly"
#     dst = f"../blender-{blender_version}{ext}"
# 
#     if os.path.exists(dst):
#         shutil.rmtree(dst)
# 
#     src = f"{cache_dir}/{blender_archive}"
#     print(f"Move {src} to {dst}")
#     shutil.move(src, dst)


def main(blender_version):

    blender_zipfile, nightly = getSuffix(blender_version)

    getBlender(blender_version, blender_zipfile, nightly)


if __name__ == "__main__":
    if "cygwin" == sys.platform:
        print(
            "ERROR, do not run this under cygwin, run it under Linux and Windows cmd!!"
        )
        exit()

    if len(sys.argv) >= 2:
        blender_rev = sys.argv[1]
    else:
        blender_rev = "2.79b"

    if re.search("-", blender_rev):
        blender_rev, _ = blender_rev.split("-")

    main(blender_rev)
