from lwo_helper import diff_files, delete_everything

def main():
    outfile0 = "tests/ref_blend/box2-uv.lwo.blend"
    outfile1 = "tests/dst_blend/box2-uv.lwo.blend"
    
    diff_files(outfile0, outfile1)

    delete_everything()


if __name__ == "__main__":
    main()
