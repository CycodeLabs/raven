from setuptools import find_packages
from setuptools import setup
from distutils import log
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
REQUIRMENTS = (HERE / "requirements.txt").read_text().splitlines()
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 7)
if CURRENT_PYTHON < REQUIRED_PYTHON:
    log.fatal("Raven requires Python V3.7 or greater.")
    sys.exit(1)


setup(
    name="raven",
    description="",
    long_description=README,
    url="https://github.com/CycodeLabs/Raven",
    project_urls={"Source": "https://github.com/CycodeLabs/Raven"},
    author="Cycode",
    license="Apache License 2.0",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Intended Audience :: Science/Research",
        "Topic :: CI/CD Security",
    ],
    install_requires=REQUIRMENTS,
    packages=find_packages(exclude=("tests", "tests.*")),
    entry_points={"console_scripts": ["raven = src.cmdline:execute"]},
)
