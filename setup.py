#!/usr/bin/python3

from setuptools import setup

#Load README.md file
with open("README.md", "r") as f:
    long_desc = f.read()

#Run setup
setup(
    long_description = long_desc,
    long_description_content_type = "text/markdown"
)