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
    from setuptools_scm.version import guess_next_dev_version
    from setuptools_scm.utils import has_command
    has_git_command = has_command('git')


    def fixed_version_scheme(version):
        """
        A fix for https://github.com/smarie/python-getversion/issues/10
        until this is fixed in setuptools_scm or in pkg_resources
        so that the dash is not removed when a pre-release version is present (e.g. 1.0.0-rc1)
        """
        # This is the bugged string would be used by the default scheme (for reference)
        # str(version.tag)

        # modify the 'pre' part only if needed
        do_hack = version.tag.is_prerelease
        if do_hack:
            # make a backup
            _version_bak = version.tag._version

            # get the various parts
            parts = _version_bak._asdict()

            # make sure we understand what we do by doing a simple copy
            clone = type(_version_bak)(**parts)
            assert clone == _version_bak, "Internal error with this version of `pkg_resources`, please report"

            # now do a mod
            parts['pre'] = ("-",) + parts['pre']
            _version_mod = type(_version_bak)(**parts)

            # and apply it
            version.tag._version = _version_mod

            # we can check that the string has been fixed correctly
            # str(version.tag)

        # create the version string as usual by applying setuptools_scm's default version scheme
        # note that despite the name, this does not increment anything if the tag is exact (no local mod)
        res = guess_next_dev_version(version)

        # undo our hack if needed
        if do_hack:
            version.tag._version = _version_bak  # noqa

        return res


    def scm_get_version_recursive_root(abs_path, initial_path):
        """
        Recursively climbs the parent folders, searching for a git root

        :param abs_path:
        :return:
        """
        try:
            res = get_version(abs_path, version_scheme=fixed_version_scheme)
        except LookupError as e:
            parent_dir = dirname(abs_path)
            if parent_dir == abs_path:
                # cannot recurse anymore
                raise ScmInformationNotFound(initial_path)
            else:
                # recurse
                return scm_get_version_recursive_root(parent_dir, initial_path=initial_path)
        else:
            return res

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
