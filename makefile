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
	. venv/bin/activate; flake8 ./ECAgent/

check-verbose: venv
	. venv/bin/activate; flake8 --show-source ./ECAgent/

dist: package

upload: dist
	. venv/bin/activate; twine upload --repository pypi dist/*

clean:
	rm -rf venv
	rm -rf dist
	find -iname "*.pyc" -delete
	rm -rf ECAgent.egg-info