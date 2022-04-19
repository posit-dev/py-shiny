#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

test_requirements = [
    "pytest>=3",
]

setup(
    author="Winston Chang",
    author_email="winston@rstudio.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="A web development framework for Python.",
    license="GNU General Public License v3",
    include_package_data=True,
    keywords="shiny",
    name="shiny",
    packages=find_packages(include=["shiny", "shiny.*"]),
    package_data={
        "shiny": ["py.typed"],
    },
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/rstudio/py-shiny",
    version="0.0.0.9001",
    zip_safe=False,
)
