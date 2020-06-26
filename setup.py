from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ECAgent",
    version="0.0.5",
    author="Brandon Gower-Winter",
    author_email="brandongowerwinter@gmail.com",
    description="An Agent-based Modelling framework based on the Entity-Component-System architectural pattern.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BrandonGower-Winter/ABMECS",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)