[![Build Status](https://travis-ci.org/douglaskastle/blender-fake-addon.svg?branch=master)](https://travis-ci.org/douglaskastle/blender-fake-addon)
[![codecov.io Code Coverage](https://img.shields.io/codecov/c/github/douglaskastle/blender-fake-addon.svg?maxAge=2592000)](https://codecov.io/github/douglaskastle/blender-fake-addon?branch=master)

# Blender - pytest - TravisCI integration

The code to shows how the `pytest` can be used inside blender to test an addon.  Once a checkin has been performed TravisCI runs the tests on the current nightly builds for blender 2.79 and 2.8.

## pytest

Blender comes with it own version of python.  When you run blender the python it uses is this one not one that has been installed on you system.  The python that blender somes with has `unittest` as a standard module.  `unittest` is a bit long in the tooth, `pytest` has started to become a lot more popular in the industry. So two things are missing that we need to get, `pip` and `pytest`.  

To install `pip` you need to fetch `get-pip.py` from this path:

`wget https://bootstrap.pypa.io/get-pip.py`

and then we explictly call the python inside blender to install `pip`:

`blender/2.79/python/bin/python3.7m get-pip.py`

this will install `pip` locally that when called will install modules into the blender version of python and not the system.

linux: `blender/2.79/python/bin/pip`
windows: `blender\2.79\python\Scripts\pip`

we use this `pip` to install pytest:

`blender/2.79/python/bin/pip install pytest`

## fake-addon

## Run tests locally

## TravisCI
