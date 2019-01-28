import sys
import pytest
from addon_helper import SetupAddon

class SetupPytest(SetupAddon):

    def pytest_configure(self, config):
        super().configure()
        config.cache.set("bpy_module", self.bpy_module)

    def pytest_unconfigure(self):
        super().unconfigure()
        print("*** test run reporting finished")


# addon = "io_import_scene_lwo.py"
# addon = "io_import_scene_lwo_1_2_edit.py"
addon = "io_import_scene_lwo"
exit_val = pytest.main(["tests"], plugins=[SetupPytest(addon)])
sys.exit(exit_val)
