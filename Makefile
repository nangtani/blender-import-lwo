BLENDER_VERSION ?= 3.0
BLENDER_ADDON ?= io_scene_lwo

default:
	@echo $(BLENDER_VERSION)
	$(MAKE) flake8
	python scripts/test_addon.py $(BLENDER_ADDON) $(BLENDER_VERSION)

all:
	python scripts/test_addon.py $(BLENDER_ADDON) 3.0
	python scripts/test_addon.py $(BLENDER_ADDON) 2.93
	python scripts/test_addon.py $(BLENDER_ADDON) 2.92
	python scripts/test_addon.py $(BLENDER_ADDON) 2.83
	python scripts/test_addon.py $(BLENDER_ADDON) 2.82
	python scripts/test_addon.py $(BLENDER_ADDON) 2.81

get:
	python3 scripts/get_blender.py 2.81
	python3 scripts/get_blender.py 2.82
	python3 scripts/get_blender.py 2.83
	python3 scripts/get_blender.py 2.92
	python3 scripts/get_blender.py 2.93
	python3 scripts/get_blender.py 3.0

flake8:
	@flake8 $(BLENDER_ADDON) --count --show-source --statistics
