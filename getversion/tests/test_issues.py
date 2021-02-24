from os.path import join, pardir

from setuptools_scm import _do_parse, Configuration, format_version
from getversion.plugin_setuptools_scm import fixed_version_scheme

from pkg_resources import parse_version as pkg_parse_version


def test_issue_10():
    # version with a prerelease
    version_str = "1.0.0-rc1"

    # Parse with pkg_resource and make sure that the issue is still there (see #10)
    pkg_res_version = pkg_parse_version(version_str)
    assert str(pkg_res_version) == '1.0.0rc1'

    # use setuptools_scm to get a version object that we can modify to introduce the bug
    config = Configuration(root=join(__file__, pardir, pardir, pardir))
    s_version = _do_parse(config)
    # --make sure that internals of `setuptools_scm` have not changed: the .tag object is a pkg_resource Version
    assert isinstance(s_version.tag, type(pkg_res_version))
    # --now lets modify the version object so as to inject the issue
    s_version.tag = pkg_res_version

    # make sure that setuptools_scm did not fix the issue yet
    pb_ver = format_version(
        s_version,
        version_scheme=config.version_scheme,
        local_scheme=config.local_scheme,
    )
    assert str(pb_ver) != version_str
    assert str(pb_ver).startswith("1.0.0rc")  # dash removed

    # make sure that with our fixed version scheme (used in our plugin) it works
    fixed_vers = format_version(
        s_version,
        version_scheme=fixed_version_scheme,
        local_scheme=config.local_scheme,
    )
    assert str(fixed_vers).startswith("1.0.0-rc")  # with the dash
