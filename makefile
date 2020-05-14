#Brandon Gower-Winter
#Image Clustering Assignment Demo

#SHELL:=/bin/bash

BIN:=./venv/bin/

install: venv
	. venv/bin/activate; pip3 install -Ur requirements.txt

venv :
	test -d venv || python3 -m venv venv --system-site-packages

check: venv
	. venv/bin/activate; pycodestyle --first ./src/ECAgent.py

check-verbose: venv
	. venv/bin/activate; pycodestyle --show-source --show-pep8 ./src/ECAgent.py

clean:
	rm -rf venv
	find -iname "*.pyc" -delete