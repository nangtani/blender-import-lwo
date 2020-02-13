one:
	python scripts/run_blender.py 2.79b

all:
#	python scripts/run_blender.py 2.78c
# 	python scripts/run_blender.py 2.79b
# 	python scripts/run_blender.py 2.80
# 	python scripts/run_blender.py 2.81a
# 	python scripts/run_blender.py 2.82
	python scripts/run_blender.py 2.83

get:
	python scripts/get_blender.py 2.78c
	python scripts/get_blender.py 2.79b
	python scripts/get_blender.py 2.80
	python scripts/get_blender.py 2.81a
	python scripts/get_blender.py 2.82
	python scripts/get_blender.py 2.83

flake8:
	@flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
