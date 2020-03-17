ADDON = "io_import_scene_lwo"

import os
import sys
try:
    import pytest
except Exception as e:
    print(e)
    sys.exit(1)

try:
    sys.path.append(os.environ["LOCAL_PYTHONPATH"])
    from addon_helper import SetupAddon
except Exception as e:
    print(e)
    sys.exit(1)


class SetupPlugin(SetupAddon):
    def pytest_configure(self, config):
        super().configure()
        config.cache.set("bpy_module", self.bpy_module)

    def pytest_unconfigure(self):
        super().unconfigure()
        print("*** test run reporting finished")

try:
    # exit_val = pytest.main(["tests/basic/test_load_lwo.py::test_load_lwo_box1", "-v", "-x", "--cov", "--cov-report", "term-missing", "--cov-report", "xml",], plugins=[SetupPlugin(ADDON)])
    extra_cmd = "--ignore=tests/lwo_nasa"
    if 'TRAVIS_BRANCH' in os.environ.keys():
        if "master" == os.environ["TRAVIS_BRANCH"] or  "develop" == os.environ["TRAVIS_BRANCH"]:
            extra_cmd = ""

    exit_val = pytest.main(
        ["tests", "-v", "-x", extra_cmd, "--cov", "--cov-report", "term", "--cov-report", "xml",],
        plugins=[SetupPlugin(ADDON)],
    )
    #exit_val = pytest.main(["tests/lwo_nasa/test_load_lwo_nasa.py", "-v", "-x", "--cov", "--cov-report", "term", "--cov-report", "xml",], plugins=[SetupPlugin(ADDON)])
    #exit_val = pytest.main(["tests/basic/test_load_lwo.py", "-v", "-x", "--cov", "--cov-report", "term", "--cov-report", "xml",], plugins=[SetupPlugin(ADDON)])
    #exit_val = pytest.main(["tests/lwo_bulk/test_load_bulk.py", "-v", "-x", "--cov", "--cov-report", "term", "--cov-report", "xml",], plugins=[SetupPlugin(ADDON)])
except Exception as e:
    print(e)
    exit_val = 1
sys.exit(exit_val)
