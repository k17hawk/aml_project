"""
author:@kumar dahal
this function is written for version controlling.
It will read long description from readme.md file
"""
#import setuptools
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
#set the initial version as 0
__version__ = "0.0.1"

REPO_NAME = "aml_project"
AUTHOR_USER_NAME = "k17hawk"
SRC_REPO = "src"
AUTHOR_EMAIL = "kumardahal536@gmail.com"

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    #for now we have only one package directory so we have given src, also it is our main src directory
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)