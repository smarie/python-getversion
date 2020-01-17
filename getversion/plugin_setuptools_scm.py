#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

from os.path import dirname, abspath


class GitCommandNotAvailable(Exception):
    def __str__(self):
        return "`git` command is not available ; please make sure that it is in your PATH."


class ScmInformationNotFound(Exception):
    def __init__(self, initial_path):
        self.path = initial_path

    def __str__(self):
        return "Unable to find SCM information (/.git or /.hg folder, typically) " \
               "in the parent folders of %s" % self.path


class SetupToolsScmNotInstalled(Exception):
    def __str__(self):
        return "`setuptools_scm` package does not seem to be available in your python environment. Please install it" \
               " to enable SCM version discovery (git, hg)."


try:
    from setuptools_scm import get_version
    from setuptools_scm.utils import has_command
    has_git_command = has_command('git')

    def scm_get_version_recursive_root(abs_path, initial_path):
        """
        Recursively climbs the parent folders, searching for a git root

        :param abs_path:
        :return:
        """
        try:
            return get_version(abs_path)
        except LookupError as e:
            parent_dir = dirname(abs_path)
            if parent_dir == abs_path:
                # cannot recurse anymore
                raise ScmInformationNotFound(initial_path)
            else:
                # recurse
                return scm_get_version_recursive_root(parent_dir, initial_path=initial_path)


    def get_version_using_setuptools_scm(module  # type: ModuleType
                                         ):
        # type: (...) -> str
        """
        get version from the source directory if it is under version control
        :param module:
        :return:
        """
        # ...using setuptools_scm if available
        if not has_git_command:
            raise GitCommandNotAvailable()
        else:
            path = abspath(module.__file__)
            return scm_get_version_recursive_root(path, initial_path=path)

except ImportError:
    # no
    def get_version_using_setuptools_scm(module  # type: ModuleType
                                         ):
        # type: (...) -> str
        raise SetupToolsScmNotInstalled()
