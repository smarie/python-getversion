# python-getversion

(hopefully) universal library to get the package version number of a python module, by combining various strategies (PEP396/version, setuptools/`pkg_resources`, PEP427/wheel, git...)

[![Python versions](https://img.shields.io/pypi/pyversions/getversion.svg)](https://pypi.python.org/pypi/getversion/) [![Build Status](https://travis-ci.org/smarie/python-getversion.svg?branch=master)](https://travis-ci.org/smarie/python-getversion) [![Tests Status](https://smarie.github.io/python-getversion/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-getversion/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-getversion/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-getversion)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-getversion/) [![PyPI](https://img.shields.io/pypi/v/getversion.svg)](https://pypi.python.org/pypi/getversion/) [![Downloads](https://pepy.tech/badge/getversion)](https://pepy.tech/project/getversion) [![Downloads per week](https://pepy.tech/badge/getversion/week)](https://pepy.tech/project/getversion) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-getversion.svg)](https://github.com/smarie/python-getversion/stargazers)

**This is the readme for developers.** The documentation for users is available here: [https://smarie.github.io/python-getversion/](https://smarie.github.io/python-getversion/)

## Want to contribute ?

Contributions are welcome ! Simply fork this project on github, commit your contributions, and create pull requests.

Here is a non-exhaustive list of interesting open topics: [https://github.com/smarie/python-getversion/issues](https://github.com/smarie/python-getversion/issues)

## Running the tests

This project uses `pytest`.

```bash
pytest -v getversion/tests/
```

You may need to install requirements for setup beforehand, using 

```bash
pip install -r ci_tools/requirements-test.txt
```

## Packaging

This project uses `setuptools_scm` to synchronise the version number. Therefore the following command should be used for development snapshots as well as official releases: 

```bash
python setup.py egg_info bdist_wheel rotate -m.whl -k3
```

You may need to install requirements for setup beforehand, using 

```bash
pip install -r ci_tools/requirements-setup.txt
```

## Generating the documentation page

This project uses `mkdocs` to generate its documentation page. Therefore building a local copy of the doc page may be done using:

```bash
mkdocs build -f docs/mkdocs.yml
```

You may need to install requirements for doc beforehand, using 

```bash
pip install -r ci_tools/requirements-doc.txt
```

## Generating the test reports

The following commands generate the html test report and the associated badge. 

```bash
pytest --junitxml=junit.xml -v getversion/tests/
ant -f ci_tools/generate-junit-html.xml
python ci_tools/generate-junit-badge.py
```

### PyPI Releasing memo

This project is now automatically deployed to PyPI when a tag is created. Anyway, for manual deployment we can use:

```bash
twine upload dist/* -r pypitest
twine upload dist/*
```
