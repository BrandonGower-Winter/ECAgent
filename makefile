#Brandon Gower-Winter
#Image Clustering Assignment Demo

#SHELL:=/bin/bash

BIN:=./venv/bin/

install: venv
	. venv/bin/activate; pip3 install -Ur requirements.txt

venv :
	test -d venv || python3 -m venv venv --system-site-packages

package: venv
	. venv/bin/activate; python setup.py sdist bdist_wheel

test: venv
	. venv/bin/activate; python -m pytest ./tests/

check: venv
	. venv/bin/activate; pycodestyle --first ./src/ECAgent/Core.py

check-verbose: venv
	. venv/bin/activate; pycodestyle --show-source --show-pep8 ./src/ECAgent/Core.py

upload: package
	. venv/bin/activate; twine upload --repository pypi dist/*

clean:
	rm -rf venv
	rm -rf dist
	find -iname "*.pyc" -delete
	rm -rf *.egg-info