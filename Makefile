BLENDER_VERSION ?= 3.3
BLENDER_ADDON ?= io_scene_lwo

default:
	@echo $(BLENDER_VERSION)
	$(MAKE) flake8
	python scripts/test_addon.py $(BLENDER_ADDON) $(BLENDER_VERSION)

all:
# 	python scripts/test_addon.py $(BLENDER_ADDON) 3.6
# 	python scripts/test_addon.py $(BLENDER_ADDON) 3.5
	python scripts/test_addon.py $(BLENDER_ADDON) 3.3
# 	python scripts/test_addon.py $(BLENDER_ADDON) 3.2
# 	python scripts/test_addon.py $(BLENDER_ADDON) 3.0
# 	python scripts/test_addon.py $(BLENDER_ADDON) 2.82

get:
# 	python3 scripts.old/get_blender.py 3.6.21
# 	python3 scripts.old/get_blender.py 3.5
	python3 scripts.old/get_blender.py 3.3
# 	python3 scripts.old/get_blender.py 3.2
# 	python3 scripts.old/get_blender.py 3.0
# 	python3 scripts.old/get_blender.py 2.82

flake8:
	@flake8 $(BLENDER_ADDON) --count --show-source --statistics
