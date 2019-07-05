# Changelog

### 0.5.1 - Bugfixes

 - fixed PyPi doc
 - `__version__` should now be available on the distributed `getversion` package.

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
