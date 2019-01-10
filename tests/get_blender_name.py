import os
import sys
import requests
import re
from bs4 import BeautifulSoup

def main(rev):
    url = "https://builder.blender.org/download"

    page = requests.get(url)    
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")

    index = ""
    for link in soup.find_all('a'):
        x = str(link.get('href'))
        # of the format blender-2.79-e6acb4fba094-linux-glibc224-x86_64.tar.bz2
        g = re.search("{0}(-\w+)-linux.+x86_64".format(rev), x)
        if g:
            index = g.group(1)
    print(index)
    
if __name__ == '__main__':
    try:
        blender_rev = sys.argv[1]
    except:
        blender_rev = "2.79"
    main(blender_rev)
