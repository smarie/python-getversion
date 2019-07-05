#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

from os.path import join, dirname

from getversion.plugin_eggs_and_wheels import read_pkg_name_from_dist_info_toplevel, read_version_from_dist_info, \
    read_version_from_egg_info


def test_dist_info():
    """
    Tests that the functions to get the package name and version from an unzipped wheel's dist-info folder work.
    :return:
    """
    path = join(dirname(__file__), 'resources', 'unzipped_wheels', 'dummy-2.9.2.dist-info')

    pkg_name = read_pkg_name_from_dist_info_toplevel(path)
    assert pkg_name == 'dummy'

    version = read_version_from_dist_info(path)
    assert version == '2.9.2'


def test_egg_info():
    """
    Tests that the functions to get the package name and version from an unzipped wheel's dist-info folder work.
    :return:
    """
    path = join(dirname(__file__), 'resources', 'unzipped_eggs', 'dummy3-0.1.0.egg-info')

    # pkg_name = read_pkg_name_from_egg_info(path)
    # assert pkg_name == 'dummy3'

    version = read_version_from_egg_info(path)
    assert version == '0.1.0'
