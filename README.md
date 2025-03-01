[![Build Status](https://travis-ci.org/nangtani/blender-import-lwo.svg?branch=master)](https://travis-ci.org/nangtani/blender-import-lwo)
[![codecov](https://codecov.io/gh/nangtani/blender-import-lwo/branch/master/graph/badge.svg)](https://codecov.io/gh/nangtani/blender-import-lwo)
[![Gitter](https://badges.gitter.im/nangtani/blender-import-lwo.svg)](https://gitter.im/nangtani/blender-import-lwo?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
# Download ADDON here:
What you see here is a project wrapped around an addon to enable testing, the addon itself is the subdirectory, `io_scene_lwo`.  If you just want the addon it is maintained in the release area:
[releases](https://github.com/nangtani/blender-import-lwo/releases)

# Blender LWO Importer

This is a [lightwave](https://www.lightwave3d.com/) importer addon for [Blender](https://www.blender.org/). 

It reads a lightwave object file, LWO, and converts it into a mesh with materials inside blender.

This design was forked from the blender-addons repo before it was removed from that [repo](https://github.com/nangtani/blender-addons/commit/31608d8ee37bd753573a10482a2514787b80f923).

* Support LWO and LWO2 format
* Support for cycles
* GUI navigation for missing images directory
* NGON support for keyhole NGONs
* PrincipleBSDF support
* LWO parsing is wholly in it's own module, no blender elements, it can be used in other non blender projects.
* Regressable tests with checked in LWO examples

## blender-addon-tester 

Tests exist for this addon. Tests are written in `pytest` and are enabled using the [`blender-addon-tester`](https://pypi.org/project/blender-addon-tester).  

This allows testing to be completed on multiple versions of blender, including the nightly builds.  This flags any changes to the Blender Addon API that breaks the addon closer to when it happens.

Current testing supports blender 3.3 through 4.5.

To run tests locally:

    `pip install blender-addon-tester`
    `python scripts\test_addon.py io_scene_lwo 3.6`

## Not supported (yet)

* Lightwave Scene files, LWS
* LWO3

## Questions or Issues

Please raise any issues or requests via the [github issues page](https://github.com/nangtani/blender-import-lwo/issues).

## LWO Specification

You can find the LWO2 format specification found [here](../../wiki/LWO2-file-format-(2001)).

# Old Addon

The original addon can be found in the official addon repos [here](https://github.com/nangtani/blender-addons-contrib/blob/b1a19799d2ec0dc320b8064d281ee81a1f018b9a/io_import_scene_lwo.py).
