# getversion

*Get the version number of any python module or package, reliably.*

[![Python versions](https://img.shields.io/pypi/pyversions/getversion.svg)](https://pypi.python.org/pypi/getversion/) [![Build Status](https://travis-ci.org/smarie/python-getversion.svg?branch=master)](https://travis-ci.org/smarie/python-getversion) [![Tests Status](https://smarie.github.io/python-getversion/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-getversion/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-getversion/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-getversion)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-getversion/) [![PyPI](https://img.shields.io/pypi/v/getversion.svg)](https://pypi.python.org/pypi/getversion/) [![Downloads](https://pepy.tech/badge/getversion)](https://pepy.tech/project/getversion) [![Downloads per week](https://pepy.tech/badge/getversion/week)](https://pepy.tech/project/getversion) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-getversion.svg)](https://github.com/smarie/python-getversion/stargazers)

Do you need a reliable way to get a version number corresponding to a python object ? `getversion` was made for this. It combines several existing strategies to cover the broadest possible set of cases. It is easily extensible so that adding new cases is extremely easy. Do not hesitate to open an [issue or a PR](https://github.com/smarie/python-getversion/issues) if the current 5 built-in strategies do not work for you!

## Motivation

Version numbers in python can be in very different places depending on the case:

 * for **modules and packages**, on the optional `__version__` attribute as recommended by [PEP396](https://www.python.org/dev/peps/pep-0396/#specification). It should be considered inherited by subpackages and submodules by default if they do not have the attribute.
 
 * for **distributed modules and packages**, on the `Version` Metadata field as indicated by [PEP345](https://www.python.org/dev/peps/pep-0345/#version), that is located:
 
    * for *built wheels distributions* ([PEP427](https://www.python.org/dev/peps/pep-0427)), on the `dist-info` [directory](https://www.python.org/dev/peps/pep-0427/#the-dist-info-directory), but also in the [dist-info folder name](https://www.python.org/dev/peps/pep-0427/#file-contents)
    * for *built eggs distributions* (legacy format from [setuptools](https://setuptools.readthedocs.io/en/latest/formats.html)), on the `egg-info` [directory](https://setuptools.readthedocs.io/en/latest/formats.html#project-metadata), but is also in the [egg-info folder name](https://setuptools.readthedocs.io/en/latest/formats.html#filename-embedded-metadata)

 * finally, for **built-in modules and packages**, the default version should be inherited from the python system version except if overridden


In addition to this, at runtime (when you need that version number), packages and modules can be

 - already imported or not
 - built and pip-installed (in debug mode or not), or simply added to the PYTHON PATH (`sys.path`)
 - non-built and added to the PYTHON PATH (`sys.path`)

This variety of settings makes it very difficult for existing solutions to tackle all aspects of this problem. `pkg_resources` is probably the best way to get it as of today (like [this](https://stackoverflow.com/questions/8880661/getting-package-version-using-pkg-resources)), but does not work for example when a package is an unzipped wheel added to the PYTHON PATH. It also does not support built-in modules.
 

## Installing

```bash
> pip install getversion
```

## Reminder: packages, modules, distributing

In python:
 - a *module* is a file ending with `.py`, containing some symbols.
 - a *package* is a folder containing a `__init__.py` file, as well as any number of subpackages and submodules.

See also [this explanation](https://www.quora.com/What-is-the-difference-between-Python-modules-packages-libraries-and-frameworks).

When you distribute python code, you distribute either a single module, or a single package. The name of this "root" module or package is the first name that appears in an import:

```python
import html         # root package 'html'
import html.parser  # submodule 'parser' of pkg 'html'
```

See [distributing python modules](https://docs.python.org/3/distributing/index.html).


## Usage

TODO


## Main features / benefits

 * **Get package version easily**: a single method will get you what you need, whatever the variety of ways needed to get the information
 * **Support for multiple strategies**: PEP396/version, setuptools/`pkg_resources`, PEP427/wheel, git...

## See Also

Concerning the strategies:

 - [PEP314/Metadata](https://www.python.org/dev/peps/pep-0314/)
 - [PEP396/\__version__](https://www.python.org/dev/peps/pep-0396/)
 - `pkg_resources` [documentation](https://setuptools.readthedocs.io/en/latest/pkg_resources.html) and [PEP365](https://www.python.org/dev/peps/pep-0365/)
 - [PEP427/wheel](https://www.python.org/dev/peps/pep-0427/)
 - [setuptools_scm](https://github.com/pypa/setuptools_scm/)
 - [stdlib_list](https://github.com/jackmaney/python-stdlib-list)

Discussion on PyPa: [here](https://github.com/pypa/setuptools/issues/1316).

Other attempts to reach the same target:

 - [app_version](https://github.com/lambdalisue/app_version)
 - [importlib_metadata](https://gitlab.com/python-devs/importlib_metadata)
 - [read_version](https://github.com/jwodder/read_version)
 
### Package versioning best practices

See [this post](https://stackoverflow.com/questions/17583443/what-is-the-correct-way-to-share-package-version-with-setup-py-and-the-package/17638236#17638236) for a start.

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-getversion](https://github.com/smarie/python-getversion)
