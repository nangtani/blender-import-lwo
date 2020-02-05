import os
import sys
sys.path.append(os.environ["LOCAL_PYTHONPATH"])
from lwo_helper import diff_files, delete_everything

def main():
# #     outfile0 = "tests/basic/ref_blend/2.80/cycles/LWO2/ngon/ngon0.lwo.blend"
# #     outfile1 = "tests/basic/dst_blend/2.80/cycles/LWO2/ngon/ngon0.lwo.blend"
# #     outfile0 = "tests/basic/ref_blend/2.80/cycles/LWO2/box/box5-ngon.lwo.blend"
# #     outfile1 = "tests/basic/dst_blend/2.80/cycles/LWO2/box/box5-ngon.lwo.blend"
#     outfile0 = "tests/basic/ref_blend/2.79/blender_render/LWO2/box/box5-ngon.lwo.blend"
#     outfile1 = "tests/basic/dst_blend/2.79/blender_render/LWO2/box/box5-ngon.lwo.blend"
#     
#     diff_files(outfile0, outfile1)
# 
#     delete_everything()


    outfile0 = "tests/basic/ref_blend/2.80/cycles/LWO2/ngon/ngon0.lwo.blend"
    outfile1 = "tests/basic/dst_blend/2.80/cycles/LWO2/ngon/ngon0.lwo.blend"
    diff_files(outfile0, outfile1)

#     delete_everything()
#     outfile0 = "tests/basic/ref_blend/2.80/cycles/LWO2/box/box5-ngon.lwo.blend"
#     outfile1 = "tests/basic/dst_blend/2.80/cycles/LWO2/box/box5-ngon.lwo.blend"
#     diff_files(outfile0, outfile1)
# 
#     delete_everything()


if __name__ == "__main__":
    main()
