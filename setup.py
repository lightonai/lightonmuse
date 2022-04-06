import pathlib
from setuptools import find_packages, setup


here = pathlib.Path(__file__).parent.resolve()

name = "lightonmuse"
description = "Python client for the LightOn Muse API"
# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')
author = "LightOn AI Research"
author_email = "support@lighton.ai"
classifiers = [
    # Trove classifiers
    # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
]

try:
    setup(
        name=name,
        description=description,
        long_description=long_description,
        author=author,
        author_email=author_email,
        url='https://github.com/lightonai/lightonmuse',
        use_scm_version=True,
        setup_requires=["setuptools_scm"],
        install_requires=["requests>=2.26.0"],
        packages=find_packages(exclude=["examples", "tests"]),
        keywords=["NLP", "API", "AI"],
        classifiers=classifiers
    )
except LookupError:
    setup(
        name=name,
        description=description,
        long_description=long_description,
        author=author,
        author_email=author_email,
        version="test",
        packages=find_packages("lightonmuse", exclude=["examples", "tests"]),
        classifiers=classifiers
    )
