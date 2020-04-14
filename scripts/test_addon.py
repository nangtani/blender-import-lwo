import os
import sys
try:
    import blender_addon_tester as BAT
except Exception as e:
    print(e)
    sys.exit(1)


def main():    
    if len(sys.argv) > 1:
        addon = sys.argv[1]
    else:
        addon = "io_import_scene_lwo"
    if len(sys.argv) > 2:
        blender_rev = sys.argv[2]
    else:
        blender_rev = "2.82a"
    
      
    local_python = os.path.join(os.getcwd(), "scripts")
    os.environ["LOCAL_PYTHONPATH"] = local_python
    #sys.path.append(os.environ["LOCAL_PYTHONPATH"])
    
    config = {"coverage": True, "tests": "tests_lite/"}
    try:
        exit_val = BAT.test_blender_addon(addon_path=addon, blender_revision=blender_rev)
    except Exception as e:
        print(e)
        exit_val = 1
    sys.exit(exit_val)

main()
