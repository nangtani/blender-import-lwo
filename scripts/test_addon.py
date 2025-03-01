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
        addon = "io_scene_lwo"
    if len(sys.argv) > 2:
        blender_rev = sys.argv[2]
    else:
        blender_rev = "3.2"

    if os.path.isdir("scripts"):
        os.environ["ADDON_TEST_HELPER"] = os.path.join(os.getcwd(), "scripts")
        # This needs to be removed when bug in run_blender is identified
        # This is needed for linux, doesn't seem to work for windows
        sys.path.append(os.environ["ADDON_TEST_HELPER"])

    extra_cmd = "--ignore=tests/lwo_nasa"
    if "TRAVIS_BRANCH" in os.environ.keys():
        if (
            "master" == os.environ["TRAVIS_BRANCH"]
            or "develop" == os.environ["TRAVIS_BRANCH"]
        ):
            # if "master" == os.environ["TRAVIS_BRANCH"]:
            extra_cmd = ""

    config = {"coverage": True, "pytest_args": extra_cmd}
    config = {"coverage": False}
    #     config = {
    #         "coverage": False,
    #         "tests": "tests/basic/test_load_lwo.py",
    #     }
    #     config = {
    #         "coverage": True,
    #         "pytest_args": "--ignore=tests/lwo_nasa",
    #     }
    try:
        exit_val = BAT.test_blender_addon(
            addon_path=addon, blender_revision=blender_rev, config=config
        )
    except Exception as e:
        print(e)
        exit_val = 1
    sys.exit(exit_val)


if __name__ == "__main__":
    main()
