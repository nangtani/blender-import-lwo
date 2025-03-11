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

lint:
	pyflakes io_scene_lwo
	ruff check io_scene_lwo

mypy:
	mypy io_scene_lwo

format:
	black io_scene_lwo

checks: format lint mypy

GIT_TAG?=1.4.7
GIT_TAGX:=$(shell echo "$(GIT_TAG)" | sed 's/\./, /g')
VERSION_FILE?=`find . -name version.py`
release:
	echo "Release v${GIT_TAG}"
# 	@grep -Po '\d\.\d\.\d' cocotbext/jtag/version.py
	git tag v${GIT_TAG} || { echo "make release GIT_TAG=${GIT_TAG}"; git tag ; exit 1; }
	sed -i '/^version/c\
version = "${GIT_TAG}"' io_scene_lwo/blender_manifest.toml
	sed -i '/\"version/c\
    "version": (${GIT_TAGX}),' io_scene_lwo/__init__.py
	sed -i '/\"blender/c\
    "blender": (2, 81, 0),' io_scene_lwo/__init__.py
	sed -i '/expect_version = (1/c\
    expect_version = (${GIT_TAGX})'  tests/basic/test_version.py
	git add io_scene_lwo/blender_manifest.toml io_scene_lwo/__init__.py tests/basic/test_version.py
	git commit --allow-empty -m "Update to version ${GIT_TAG}"
	git tag -f v${GIT_TAG}
	git push && git push --tags
# 	sed -i '/^version/c\
# version = "${GIT_TAG}"
# ' io_scene_lwo/blender_manifest.toml

xx:	
	sed -i '/^version/c\
version = "${GIT_TAG}"' io_scene_lwo/blender_manifest.toml
	sed -i '/\"version/c\
    "version": (${GIT_TAGX}),' io_scene_lwo/__init__.py
	sed -i '/\"blender/c\
    "blender": (2, 81, 0),' io_scene_lwo/__init__.py
	sed -i '/expect_version = (1/c\
    expect_version = (${GIT_TAGX})'  tests/basic/test_version.py
# 	sed -i 'expect_version//c\
#     expect_version = (${GIT_TAGX}),' tests/basic/test_version.py
