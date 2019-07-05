#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

from os.path import dirname, abspath


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


def get_version_using_setuptools_scm(module  # type: ModuleType
                                     ):
    # type: (...) -> str
    """
    get version from the source directory if it is under version control
    :param module:
    :return:
    """
    # ...using setuptools_scm if available
    return scm_get_version_recursive_root(abspath(module.__file__))

    # if not isinstance(s4err, str):
    #     warn(" - (4) using setuptools_scm to find the svn/git version raised an error : [{}] {}"
    #          "".format(type(s4err).__name__, s4err))
    # else:
    #     warn(" - (4) impossible to locate the package in order to find the svn/git version: {}"
    #          "".format(s4err))
