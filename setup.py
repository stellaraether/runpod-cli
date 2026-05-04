import os
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "runpod_cli", "__init__.py")) as f:
    version = re.search(r'__version__ = "([^"]+)"', f.read()).group(1)

setup(
    name="runpod-cli",
    version=version,
    description="CLI tool for RunPod serverless endpoints",
    author="Lunan Li",
    author_email="lunan@stellaraether.com",
    url="https://github.com/stellaraether/runpod-cli",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "requests>=2.27.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "runpod=runpod_cli.cli:cli",
        ],
    },
    data_files=[
        ("share/runpod-cli", ["README.md"]),
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
