BIN:=./venv/bin/

ACTIVATE:=. venv/bin/activate;

install: venv
	$(ACTIVATE) pip3 install -Ur requirements_dev.txt

venv :
	test -d venv || python3 -m venv venv

package: venv
	$(ACTIVATE) python setup.py sdist bdist_wheel

test: venv
	$(ACTIVATE) python -m pytest ./tests/

test-coverage: venv
	$(ACTIVATE) python -m pytest --cov=ECAgent tests/

check: venv
	. venv/bin/activate; flake8 ./ECAgent/ --ignore=E501,W503

check-verbose: venv
	$(ACTIVATE) flake8 --show-source ./ECAgent/ --ignore=E501,W503

dist: package

upload: dist
	$(ACTIVATE) twine upload --repository pypi dist/*

prepare_patch:
	$(ACTIVATE) python changelogger.py 2

prepare_minor_update:
	$(ACTIVATE) python changelogger.py 1

prepare_major_update:
	$(ACTIVATE) python changelogger.py 0

clean:
	rm -rf venv
	rm -rf dist
	find -iname "*.pyc" -delete
	rm -rf ECAgent.egg-info