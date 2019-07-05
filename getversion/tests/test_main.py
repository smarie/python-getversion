#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

import sys
from importlib import import_module
from os.path import dirname, join, pardir

import pytest
from pytest_cases import pytest_fixture_plus, fixture_union
from setuptools_scm import get_version

import getversion
from getversion import get_module_version


THIS_DIR = dirname(__file__)
RESOURCES_DIR = join(THIS_DIR, 'resources')
RESOURCES_EGGS_DIR = join(RESOURCES_DIR, 'unzipped_eggs')
RESOURCES_WHEELS_DIR = join(RESOURCES_DIR, 'unzipped_wheels')

sys.path.insert(0, RESOURCES_DIR)
sys.path.insert(0, RESOURCES_EGGS_DIR)
sys.path.insert(0, RESOURCES_WHEELS_DIR)

python_sys_version = sys_version = '.'.join([str(v) for v in sys.version_info])


@pytest_fixture_plus
@pytest.mark.parametrize("module_name", [
                                         # 'html',  , not in py2
                                         # 'html.entities',   , not in py2
                                         'collections',
                                         'xml',
                                         'xml.dom',
                                         'xml.dom.minidom',
                                         # 'multiprocessing.connection', not in py2
                                         # 'os.path' failing, TODO
                                         ])
def builtin_module_and_submodule(module_name):
    """
    These modules have a valid __version__ attribute
    :param module_name:
    :return:
    """
    try:
        module = sys.modules[module_name]
    except KeyError:
        module = import_module(module_name)

    return module, python_sys_version


@pytest_fixture_plus
@pytest.mark.parametrize("module_name", ['re', 'json',
                                         # 'numpy', 'pandas',
                                         'dummy2.subpkg_with_version',
                                         'dummy2.subpkg_with_version.submodule_with_version'])
def module_with_version_attr(module_name):
    """
    These modules have a valid __version__ attribute
    :param module_name:
    :return:
    """
    try:
        module = sys.modules[module_name]
    except KeyError:
        module = import_module(module_name)

    return module, module.__version__


@pytest_fixture_plus
@pytest.mark.parametrize("module_name,root_module_name", [('json.encoder', 'json'),
                                                          # ('numpy.testing', 'numpy'),
                                                          # ('pandas.testing', 'pandas'),
                                                          # ('pandas.core', 'pandas'),
                                                          # ('pandas.core.api', 'pandas'),
                                                          ('dummy2.subpkg_no_version', 'dummy2'),
                                                          ('dummy2.submodule_no_version', 'dummy2'),
                                                          ('dummy2.subpkg_with_version.submodule_no_version', 'dummy2.subpkg_with_version')
                                                          ])
def submodule_in_pkg_with_version_attr(module_name, root_module_name):
    """
    These modules have a valid __version__ attribute
    :param module_name:
    :return:
    """
    try:
        module = sys.modules[module_name]
    except KeyError:
        module = import_module(module_name)

    try:
        root_module = sys.modules[root_module_name]
    except KeyError:
        root_module = import_module(root_module_name)

    return module, root_module.__version__


@pytest_fixture_plus
@pytest.mark.parametrize("module_name,expected_version", [('dummy', '2.9.2'),
                                                          ('dummy3', '0.1.0'),
                                                          ('dummy3b', '1.2.3'),
                                                          ('dummy4', '1.1.1'),
                                                          ], ids=lambda x: x[0])
def unzipped_wheel_or_egg(module_name, expected_version):
    try:
        module = sys.modules[module_name]
    except KeyError:
        module = import_module(module_name)

    return module, expected_version


@pytest_fixture_plus
def self_uninstalled_git():
    expected_version = get_version(join(getversion.__file__, pardir, pardir))
    return getversion, expected_version


# Create the union of all cases
mod = fixture_union("mod", [builtin_module_and_submodule,
                            module_with_version_attr,
                            submodule_in_pkg_with_version_attr,
                            unzipped_wheel_or_egg,
                            self_uninstalled_git],
                    unpack_into="module, expected_version")

# @pytest_fixture_plus
# @cases_data(module=test_main_cases)
# def mod(case_data):
#     return case_data.get()
#
#
# module, expected_version = unpack_fixture("module, expected_version", mod)


def test_modules_version(module, expected_version):
    found_version, detailed_results = get_module_version(module)
    try:
        assert found_version == expected_version
    finally:
        print(detailed_results)
