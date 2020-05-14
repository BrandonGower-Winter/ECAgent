#Brandon Gower-Winter
#Image Clustering Assignment Demo

SHELL:=/bin/bash

install:
	test -d venv || python3 -m venv venv --system-site-packages
	. venv/bin/activate; pip3 install -Ur requirements.txt

clean:
	rm -rf venv
	find -iname "*.pyc" -delete