# Changelog

### 0.5.5 - Own `__version__` was incorrect

Fixed [#4](https://github.com/smarie/python-getversion/issues/4).

### 0.5.4 - Fixed bug in case of package both installed and in the path

Fixed bug (incorrect version number) happening when a package is both installed and available on python path. This typically happens when a developer is working on a new version of a package while an older version is already installed. Fixes [#3](https://github.com/smarie/python-getversion/issues/3).

### 0.5.3 - Self `__version__`

`__version__` should now be available on the distributed `getversion` package.

### 0.5.0 - First public version

Simplified design: now a single `get_module_version` function is the entry point and compiles 4 strategies:

 - `__version__` attribute
 - built-in module using `stdlib_list`
 - unzipped wheel & unzipped egg
 - git scm using `setuptools_scm`

### 0.4.0 - extracted

First version extracted from private industrial project. Most important legacy changelog entries for reference:

 * Fixed a version detection bug happening when there is a version conflict in the pip environment (for example when package A depends on package B with version `<=1.0.0`, and the found B has version `1.1.0`).
 * The version is now correctly detected even if it is a source project and an old egg-info folder with wrong version is present in filesystem.
 * Bug fix: reading version from unzipped wheel
 * Various bug fixes in module version handling
 * Improved version detection algorithm when relying on git, in `get_pkg_version_from_module`
 * new method `get_pkg_version_from_module` in `utils_modules.py`
 * new module `utils_version_handling.py` for everything related to versions.
