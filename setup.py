import json

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('package.json') as json_file:
    data = json.load(json_file)

data.update({
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
    'packages': find_packages()
})

setup(**data)