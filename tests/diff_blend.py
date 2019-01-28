from lwo_helper import diff_files

def main():
    outfile0 = "tests/ref_blend/box1.lwo.blend"
    outfile1 = "tests/dst_blend/box1.lwo.blend"
    
    diff_files(outfile0, outfile1)



if __name__ == "__main__":
    main()
