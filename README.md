[![Build Status](https://travis-ci.org/nangtani/blender-import-lwo.svg?branch=master)](https://travis-ci.org/nangtani/blender-import-lwo)
[![codecov](https://codecov.io/gh/nangtani/blender-import-lwo/branch/master/graph/badge.svg)](https://codecov.io/gh/nangtani/blender-import-lwo)

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

Tests exist for this addon. Tests are written in `pytest` and are enabled using the `[blender-addon-tester](https://pypi.org/project/blender-addon-tester)`.  

This allows testing to be completed on multiple versions of blender, including the nightly builds.  This flags any changes to the Blender Addon API that breaks the addon closer to when it happens.

Current testing support blender 2.78 through 2.90.

To run tests locally:

    `pip install blender-addon-tester`
    `python scripts\test_addon.py io_scene_lwo 2.82a`

## Not supported (yet)

* Lightwave Scene files, LWS
* LWO3

## Questions or Issues

Please raise any issues or requests via the [github issues page](https://github.com/nangtani/blender-import-lwo/issues).

## LWO Specification

You can find the LWO2 format specification found [here](./wiki/LWO2-file-format-(2001)).
