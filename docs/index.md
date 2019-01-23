# getversion

[![Build Status](https://travis-ci.org/smarie/python-getversion.svg?branch=master)](https://travis-ci.org/smarie/python-getversion) [![Tests Status](https://smarie.github.io/python-getversion/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-getversion/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-getversion/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-getversion) [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://smarie.github.io/python-getversion/) [![PyPI](https://img.shields.io/badge/PyPI-getversion-blue.svg)](https://pypi.python.org/pypi/getversion/)

(hopefully) universal library to get the package version number of a python module, by combining various strategies (PEP396/version, setuptools/`pkg_resources`, PEP427/wheel, git...)

## Installing

```bash
> pip install getversion
```

## Usage

TODO

## Main features / benefits

 * **Get package version easily**: a single method will get you what you need, whatever the variety of ways needed to get the information
 * **Support for multiple strategies**: PEP396/version, setuptools/`pkg_resources`, PEP427/wheel, git...

## See Also

Concerning the strategies:
 - [PEP396/__version__](https://www.python.org/dev/peps/pep-0396/)
 - [PEP365/pkg_resources](https://www.python.org/dev/peps/pep-0365/)
 - [pkg_resources documentation](https://setuptools.readthedocs.io/en/latest/pkg_resources.html)
 - [PEP427/wheel](https://smarie.github.io/pytest-patterns/)
 - TODO for other strategies...

Other attempts to reach the same target:
 - [app_version](https://github.com/lambdalisue/app_version)
 - [read_version](https://github.com/jwodder/read_version)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-getversion](https://github.com/smarie/python-getversion)
