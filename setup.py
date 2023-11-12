from os import getenv
from setuptools import find_packages
from setuptools import setup
from distutils import log
import pathlib
import sys


__version__ = getenv("RAVEN_VERSION", "0.0.0")

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
REQUIRMENTS = (HERE / "requirements.txt").read_text().splitlines()
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 9)
if CURRENT_PYTHON < REQUIRED_PYTHON:
    log.fatal("Raven requires Python V3.9 or greater.")
    sys.exit(1)


setup(
    name="raven-cycode",
    version=__version__,
    description="RAVEN (Risk Analysis and Vulnerability Enumeration for CI/CD)",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/CycodeLabs/raven",
    project_urls={"Source": "https://github.com/CycodeLabs/raven"},
    author=["Cycode <research@cycode.com>"],
    keywords=["cycode", "raven", "security", "ci/cd"],
    license="Apache License 2.0",
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
    ],
    install_requires=REQUIRMENTS,
    packages=find_packages(exclude=("tests", "tests.*")),
    entry_points={"console_scripts": ["raven = src.cmdline:execute"]},
)
