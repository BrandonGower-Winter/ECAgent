BIN:=./venv/bin/

ACTIVATE:=. venv/bin/activate;

install: venv
	$(ACTIVATE) pip3 install -Ur requirements.txt

venv :
	test -d venv || python3 -m venv venv --system-site-packages

package: venv
	$(ACTIVATE) python setup.py sdist bdist_wheel

test: venv
	$(ACTIVATE) python -m pytest ./tests/

test-coverage: venv
	$(ACTIVATE) python -m pytest --cov=ECAgent tests/

check: venv
	. venv/bin/activate; flake8 ./ECAgent/

check-verbose: venv
	$(ACTIVATE) flake8 --show-source ./ECAgent/

dist: package

upload: dist
	$(ACTIVATE) twine upload --repository pypi dist/*

clean:
	rm -rf venv
	rm -rf dist
	find -iname "*.pyc" -delete
	rm -rf ECAgent.egg-info