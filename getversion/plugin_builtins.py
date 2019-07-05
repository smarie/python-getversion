#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

import sys

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

from stdlib_list import stdlib_list


@lru_cache(maxsize=1)
def get_builtin_module_list():
    return stdlib_list('.'.join([str(v) for v in sys.version_info[0:2]]))


@lru_cache(maxsize=-1)
def is_builtin(module_name):
    ref_list = get_builtin_module_list()
    return module_name in ref_list


def get_builtin_module_version(module  # type: ModuleType
                               ):
    # type: (...) -> str
    """
    It the module is in the list of builtin module names, the python version is returned as suggested by PEP396
    See https://www.python.org/dev/peps/pep-0396/#specification

    :param module:
    :return:
    """
    if module.__name__ in sys.builtin_module_names \
            or is_builtin(module.__name__):  # `imp.is_builtin` also works but maybe less efficient
        # what about this ?
        # from platform import python_version
        # python_version()
        # https://stackoverflow.com/a/25477839/7262247

        # full python version
        sys_version = '.'.join([str(v) for v in sys.version_info])
        return sys_version
    else:
        raise ValueError("Module %s is not a built-in module" % module.__name__)
