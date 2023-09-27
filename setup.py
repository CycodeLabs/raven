from setuptools import find_packages
from setuptools import setup
import pathlib
from os import path
import sys

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
REQUIRMENTS = (HERE / path.join("src", "requirements.txt")).read_text().splitlines()
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 7)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================
This version of Requests requires at least Python {}.{}, but
you're trying to install it on Python {}.{}. To resolve this,
consider upgrading to a supported Python version.

If you can't upgrade your Python version, you'll need to
pin to an older version of Requests (<2.28).
""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
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
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["raven = main:main"]},
    scripts=["src/main.py"],
)
