import sys
import pytest
from addon_helper import zip_addon, copy_addon, cleanup


class SetupPlugin(object):
    def __init__(self, addon):
        self.addon = addon

    def pytest_configure(self, config):
        (self.bpy_module, self.zfile) = zip_addon(self.addon)
        copy_addon(self.bpy_module, self.zfile)
        config.cache.set("bpy_module", self.bpy_module)

    def pytest_unconfigure(self):
        cleanup(self.addon, self.bpy_module)
        print("*** test run reporting finished")


addon = "io_import_scene_lwo.py"
# addon = "io_import_scene_lwo_1_2_edit.py"
exit_val = pytest.main(["tests"], plugins=[SetupPlugin(addon)])
sys.exit(exit_val)
