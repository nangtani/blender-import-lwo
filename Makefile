
BLENDER_VERSION ?= 2.82a

default:
	@echo $(BLENDER_VERSION)
	$(MAKE) flake8
	python3 scripts/run_blender.py $(BLENDER_VERSION)

all:
	python3 scripts/run_blender.py 2.78c
	python3 scripts/run_blender.py 2.79b
	python3 scripts/run_blender.py 2.80
	python3 scripts/run_blender.py 2.81a
	python3 scripts/run_blender.py 2.82a
	python3 scripts/run_blender.py 2.83

get:
	python3 scripts/get_blender.py 2.78c
	python3 scripts/get_blender.py 2.79b
	python3 scripts/get_blender.py 2.80
	python3 scripts/get_blender.py 2.81a
	python3 scripts/get_blender.py 2.82a
	python3 scripts/get_blender.py 2.83

flake8:
	@flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	#@flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
