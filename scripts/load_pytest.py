import os
import sys
import pytest
try:
    sys.path.append(os.environ["LOCAL_PYTHONPATH"])
    from addon_helper import SetupAddon
except Exception as e:
    print(e)
    sys.exit(1)

class SetupPytest(SetupAddon):

    def pytest_configure(self, config):
        super().configure()
        config.cache.set("bpy_module", self.bpy_module)

    def pytest_unconfigure(self):
        super().unconfigure()
        print("*** test run reporting finished")


addon = "io_import_scene_lwo"
try:
    exit_val = pytest.main(["tests"], plugins=[SetupPytest(addon)])
except Exception as e:
    print(e)
    exit_val = 1
sys.exit(exit_val)
