from importlib import import_module
from json import load
from os import scandir
from os.path import dirname, abspath, join, pardir, exists
from warnings import warn

import sys

from typing import Dict


def get_module_name_from_cls(cls):
    """
    Returns the module name from a class.

    :param cls:
    :return:
    """
    mod = cls.__module__
    if mod == '__main__':
        mod = None
        warn("class {0:} seems to have been defined in the main file; unfortunately this means that it's module/import"
             " path is unknown, so you might have to provide cls_lookup_map when decoding".format(cls))
    return mod


def get_cls_from_instance_type(mod, name, cls_lookup_map: Dict = None):
    """
    Returns a class from a module and class name. If the module is None, the

    :param mod:
    :param name:
    :param cls_lookup_map:
    :return:
    """
    cls_lookup_map = cls_lookup_map or dict()

    cls = None
    if mod is not None:
        imp_err = None

        try:
            # First try to import the module
            # module_ = __import__(module_name)  this was not importing correctly
            module = import_module('{0:}'.format(mod, name))
        except ImportError as err:
            imp_err = 'encountered import error "{0:}" while importing "{1:}" to decode a json file; perhaps ' \
                      'it was encoded in a different environment where {1:}.{2:} was available'.format(err, mod, name)
        else:
            # Then try to find the class in the module
            if hasattr(module, name):
                cls = getattr(module, name)
            else:
                imp_err = 'imported "{0:}" but could find "{1:}" inside while decoding a json file (found {2:}' \
                          ''.format(module, name, ', '.join(attr for attr in dir(module) if not attr.startswith('_')))

        # Handle errors
        if imp_err:
            if name in cls_lookup_map:
                cls = cls_lookup_map[name]
            else:
                raise ImportError(imp_err)

    else:
        try:
            # Try to import from main
            cls = getattr((__import__('__main__')), name)

        except (ImportError, AttributeError):
            if name not in cls_lookup_map:
                raise ImportError('class {0:s} seems to have been exported from the main file, which means it has no '
                                  'module/import path set; you need to provide cls_lookup_map which maps names '
                                  'to classes'.format(name))
            cls = cls_lookup_map[name]

    return cls


def get_pkg_version_from_module(module) -> str:
    """
    Helper method to get the version from a module. The following techniques are tried:
     - detect explicit __version__ tag on parent package
     - try to get the version from the package info using distutils (this works even for pip install -e .)
     - Try to get version from the source directory using setuptools_scm

    :param module:
    :return:
    """

    if module == '__main__':
        # *******  __main__ module / terminal
        warn("A None schema_version has been provided but the calling module is __main__: it has no version")
        return None
    elif module.__name__.startswith('.'):
        # ******* Relative module
        warn("A None schema_version has been provided but the calling module is a relative one ({}): it is not "
             "possible to retrieve its parent package".format(module.__name__))
        return None
    else:
        # ******* 'Normal' module

        # find parent package
        pkg = sys.modules[module.__name__.split('.')[0] or '__main__']

        # find the version of the distribution it comes from

        # (1) look for an explicit version tag
        if hasattr(pkg, '__version__'):
            return pkg.__version__

        # (2) try to get the version from the package info (this works even for pip install -e .)
        # noinspection PyBroadException
        try:
            # noinspection PyUnresolvedReferences
            import pkg_resources  # this is part of setuptools

            # First get the distribution
            # -- That one could fail in case of dependencies version conflict
            # pkg_dist = pkg_resources.require(pkg.__name__)[0]
            pkg_dist = pkg_resources.get_distribution(pkg.__name__)

            # if there is an old egg-info in the folder, the version will be that one, even if not installed!
            if exists(join(pkg_dist.location, pkg.__name__ + ".egg-info")):
                raise Exception("There is a '%s' folder in the package location so it seems to be a source project "
                                "that is not pip-installed. pkg_resources will therefore be ignored "
                                "to find the version" % (pkg.__name__ + ".egg-info"))

            # Finally return the version number
            return pkg_dist.version

        except ImportError as e:
            # could not import setuptools...
            s2err = e
        except Exception as e:  # typically a <DistributionNotFound>
            # this may happen if the module has not been even locally installed with "pip install ."
            # for example a dynamic dependency in pycharm
            s2err = e

        # (3) Try to get version from the source directory in case it is an unpacked wheel
        # Note: we could rely on pkginfo (http://pythonhosted.org/pkginfo) but it does not yet handle unzipped wheels
        if hasattr(pkg, '__path__'):
            search_dir = join(pkg.__path__[0], pardir)
            it = scandir(search_dir)
            try:
                for entry in it:
                    # TODO see https://www.python.org/dev/peps/pep-0427/#file-contents
                    if entry.is_dir() and entry.name.endswith('dist-info'):
                        if read_pkg_name_from_dist_info(entry.path) == pkg.__name__:
                            # FOUND !
                            return read_version_from_dist_info(entry.path)
                s3err = None
            except Exception as e:
                s3err = e
            finally:
                # end iterator
                for _ in it:
                    pass
        else:
            s3err = "pkg has no __path__"

        # (4) Try to get version from the source directory if it is under version control...
        if hasattr(pkg, '__file__'):
            try:
                # ...using setuptools_scm if available
                return scm_get_version_recursive_root(abspath(pkg.__file__))
            except ImportError as e:
                s4err = e
            except LookupError as e:
                s4err = LookupError("Unable to get a valid git version by recursively using 7"
                                    "setuptools_scm.get_version() on all parent folders until drive root, of {}"
                                    "".format(abspath(pkg.__file__)))
        else:
            s4err = 'pkg has no __file__'

    warn("A None schema_version has been provided but it is not possible to get the version from the calling module's "
         "package ({}). Outcome of each strategy is printed below".format(pkg))
    warn(" - (1) hasattr(pkg, '__version__') returned False")
    warn(" - (2) pkg_resources.require(pkg.__name__)[0].version raised [{}] - {}".format(type(s2err).__name__, s2err))
    if s3err is None:
        warn(" - (3) this package does not seem to come from an unzipped wheel file: no dist-info folder could be found"
             " next to the package __path__, for which contents of 'top_level.txt' matches the package name")
    elif isinstance(s3err, str):
        warn(" - (3) impossible to locate the package in order to check if if comes from an unzipped wheel: {}"
             "".format(s3err))
    else:
        warn(" - (3) this package seems to come from an unzipped wheel file but error while reading version from "
             "metadata.json inside the dist-info folder: [{}] - {}".format(type(s3err).__name__, s3err))
    if not isinstance(s4err, str):
        warn(" - (4) using setuptools_scm to find the svn/git version raised an error : [{}] {}"
             "".format(type(s4err).__name__, s4err))
    else:
        warn(" - (4) impossible to locate the package in order to find the svn/git version: {}"
             "".format(s4err))


def read_pkg_name_from_dist_info(dist_info_folder_path):
    """
    Returns the package name from a dist-info folder

    :param dist_info_folder_path:
    :return:
    """
    top_level_file = join(dist_info_folder_path, 'top_level.txt')
    with open(top_level_file, 'rt') as f:
        desc_name = f.read()

    return desc_name.strip()


def read_version_from_dist_info(dist_info_folder_path):
    """
    Tries to find the version from pkg with provided name by inspecting the contents of the dist-info folder.

    :param dist_info_folder_path:
    :param pkg_name:
    :return:
    """

    # First: rely on METADATA file
    metadata_file = join(dist_info_folder_path, 'METADATA')
    if exists(metadata_file):
        with open(metadata_file, 'rt') as f:
            for line in f.readlines():
                if line.startswith("Version:"):
                    return line[8:].strip()
        raise ValueError("METADATA file was found in dist-info folder but does not contain any Version")
    else:
        # Just in case: support metadata.json file if present
        # But it is not always present nor standard: https://github.com/pypa/wheel/issues/195
        metadata_file_json = join(dist_info_folder_path, 'metadata.json')
        if exists(metadata_file_json):
            with open(metadata_file_json, 'rt') as f:
                dct = load(f)
            return dct['version']
        else:
            raise FileNotFoundError("No METADATA not metadata.json file could be found in what seems to be an "
                                    "unzipped package distribution")


def scm_get_version_recursive_root(abs_path):
    """
    Recursively climbs the parent folders, searching for a git root

    :param abs_path:
    :return:
    """
    # noinspection PyUnresolvedReferences
    from setuptools_scm import get_version
    try:
        return get_version(abs_path)
    except LookupError as e:
        parent_dir = dirname(abs_path)
        if parent_dir == abs_path:
            # cannot recurse anymore
            raise e
        else:
            # recurse
            return scm_get_version_recursive_root(parent_dir)


def get_jsonstaxx_version() -> str:
    """
    Returns the version of this package (jsonstaxx)
    :return:
    """
    import jsonstaxx
    # noinspection PyTypeChecker
    return get_pkg_version_from_module(jsonstaxx)
