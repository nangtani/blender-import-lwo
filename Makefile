BLENDER_VERSION ?= 3.6
BLENDER_ADDON ?= io_scene_lwo

default:
	@echo $(BLENDER_VERSION)
	$(MAKE) flake8
	python scripts/test_addon.py $(BLENDER_ADDON) $(BLENDER_VERSION)

all:
	python scripts/test_addon.py $(BLENDER_ADDON) 3.3
	python scripts/test_addon.py $(BLENDER_ADDON) 3.6
	python scripts/test_addon.py $(BLENDER_ADDON) 4.3
	python scripts/test_addon.py $(BLENDER_ADDON) 4.4
	python scripts/test_addon.py $(BLENDER_ADDON) 4.5

# get:
# # 	python3 scripts.old/get_blender.py 3.6.21
# # 	python3 scripts.old/get_blender.py 3.5
# 	python3 scripts.old/get_blender.py 3.3
# # 	python3 scripts.old/get_blender.py 3.2
# # 	python3 scripts.old/get_blender.py 3.0
# # 	python3 scripts.old/get_blender.py 2.82

flake8:
	@flake8 $(BLENDER_ADDON) --count --show-source --statistics

GIT_TAG?=0.10.0
VERSION_FILE?=`find . -name version.py`
release:
	echo "Release v${GIT_TAG}"
# 	@grep -Po '\d\.\d\.\d' cocotbext/jtag/version.py
	git tag v${GIT_TAG} || { echo "make release GIT_TAG=${GIT_TAG}"; git tag ; exit 1; }
	echo "__version__ = \"${GIT_TAG}\"" > ${VERSION_FILE}
	git add ${VERSION_FILE}
	git commit --allow-empty -m "Update to version ${GIT_TAG}"
	git tag -f v${GIT_TAG}
	git push && git push --tags
