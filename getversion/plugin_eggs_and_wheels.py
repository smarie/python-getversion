#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

try:
    from os import scandir
except ImportError:
    from scandir import scandir

import re
from os.path import exists, join, pardir, abspath

try: # python 3
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def read_pkg_name_from_dist_info_toplevel(dist_info_folder_path):
    """
    Returns the package name from a dist-info folder

    :param dist_info_folder_path:
    :return:
    """
    top_level_file = join(dist_info_folder_path, 'top_level.txt')
    with open(top_level_file, 'rt') as f:
        desc_name = f.read()

    return desc_name.strip()


def _read_version_from_metadata_file(metadata_file):
    """
    Utility to parse a metadata file and extract the version
    :param metadata_file:
    :return:
    """
    if exists(metadata_file):
        with open(metadata_file, 'rt') as f:
            for line in f.readlines():
                if line.startswith("Version:"):
                    return line[8:].strip()
        raise ValueError("Metadata file was found in dist-info folder but does not contain any Version: %s"
                         % abspath(metadata_file))


def read_version_from_dist_info(dist_info_folder_path):
    """
    Tries to find the version from pkg with provided name by inspecting the contents of the dist-info folder.

    :param dist_info_folder_path:
    :param pkg_name:
    :return:
    """

    # First: rely on METADATA file
    metadata_file = join(dist_info_folder_path, 'METADATA')
    return _read_version_from_metadata_file(metadata_file)
    # else:
    #     # Just in case: support metadata.json file if present
    #     # But it is not always present nor standard: https://github.com/pypa/wheel/issues/195
    #     metadata_file_json = join(dist_info_folder_path, 'metadata.json')
    #     if exists(metadata_file_json):
    #         with open(metadata_file_json, 'rt') as f:
    #             dct = load(f)
    #         return dct['version']
    #     else:
    #         raise FileNotFoundError("No METADATA not metadata.json file could be found in what seems to be an "
    #                                 "unzipped package distribution")


def read_version_from_egg_info(egg_info_folder_path):
    metadata_file = join(egg_info_folder_path, 'PKG-INFO')
    return _read_version_from_metadata_file(metadata_file)


def get_unzipped_wheel_or_egg_version(module  # type: ModuleType
                                      ):
    # type: (...) -> str
    """
    Try to get version from the source directory in case it is an unzipped wheel or egg, added manually to the path.
    Indeed setuptools' pkg_resources does not seem to support it.

    See PEP427 Wheel binary package format (https://www.python.org/dev/peps/pep-0427/#file-contents)
    And EGG format: https://setuptools.readthedocs.io/en/latest/formats.html#filename-embedded-metadata

    Note: we could rely on pkginfo (http://pythonhosted.org/pkginfo) but it does not seem to handle unzipped wheels

    :param module:
    :return:
    """
    # search dir is the parent folder
    search_dir = join(module.__path__[0], pardir)

    # scan the directory for a file matching pattern {distribution}-{version}.dist-info/
    # as suggested by https://www.python.org/dev/peps/pep-0427/#file-contents
    #
    # or matching the egg equivalent
    # https://setuptools.readthedocs.io/en/latest/formats.html#filename-embedded-metadata
    module_name = module.__name__

    # patterns to match
    distinfo_pattern = re.compile("%s-(?P<version>[^-]*)\\.dist-info" % module_name)
    egginfo_pattern = re.compile("%s(-(?P<version>[^-]*?)(-py(?P<pyver>[^-]*?)(-(?P<platform>[^-]*?))?)?)?\\.egg-info"
                                 % module_name)
    it = scandir(search_dir)
    try:
        for entry in it:
            if entry.is_dir():
                distinfo_match = distinfo_pattern.match(entry.name)
                if distinfo_match is not None:
                    # WHEEL
                    version = distinfo_match.groupdict()['version']
                    if len(version) > 0:
                        return version
                    else:
                        # slower because we have to open the metadata file
                        return read_version_from_dist_info(entry.path)

                else:
                    egginfo_match = egginfo_pattern.match(entry.name)
                    if egginfo_match is not None:
                        # EGG
                        version = egginfo_match.groupdict()['version']
                        if version is not None and len(version) > 0:
                            return version
                        else:
                            return read_version_from_egg_info(entry.path)

    finally:
        # end iterator
        for _ in it:
            pass

    raise FileNotFoundError("No file matching egg-info or dist-info name patterns found in directory: %s"
                            % search_dir)
    #     if s3err is None:
    #         warn(" - (3) this package does not seem to come from an unzipped wheel file: no dist-info folder could be found"
    #              " next to the package __path__, for which contents of 'top_level.txt' matches the package name")
    #     elif isinstance(s3err, str):
    #         warn(" - (3) impossible to locate the package in order to check if if comes from an unzipped wheel: {}"
    #              "".format(s3err))
    #     else:
    #         warn(" - (3) this package seems to come from an unzipped wheel file but error while reading version from "
    #              "metadata.json inside the dist-info folder: [{}] - {}".format(type(s3err).__name__, s3err))
