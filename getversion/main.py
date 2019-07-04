from collections import OrderedDict
from functools import lru_cache
from itertools import chain
from os.path import abspath, join, exists
import sys
from types import ModuleType

from stdlib_list import stdlib_list

from getversion.plugin_eggs_and_wheels import get_unzipped_wheel_or_egg_version
from getversion.plugin_setuptools_scm import scm_get_version_recursive_root

try:  # python 3.5+
    from typing import Union, Iterable, Callable
except ImportError:
    pass


def get_version(thing,  # type: Union[ModuleType]
                ):
    """
    Utility method to return the version of various type of objects
    :return:
    """
    if isinstance(thing, ModuleType):
        return get_module_version(thing)
    # elif isinstance(thing, str):
    #     if thing == '__main__':
    #         # *******  __main__ module / terminal
    #         warn("The module is __main__: it has no version")
    #         return None
    else:
        raise NotImplementedError("``get_version` is not implemented for instances of <%s> (received: %s)"
                                  "" % (type(thing).__name__, thing))


# class VersionGetter(ABC):
#     """
#     Abstract API that version getting strategies should implement
#     """
#     __slots__ = ()
#
#     @abstractmethod
#     def supports_submodules(self):
#         """
#
#         :return: True if the method can be called on a submodule, False if requires a package (root module)
#         """
#
#     @abstractmethod
#     def get_version(self,
#                     module  # type: ModuleType
#                     ):
#         # type: (...) -> str
#         """
#
#         :return: a string representing the version
#         """


class ModuleVersionNotFound(Exception):
    """
    Final exception Raised by get_module_version when the version of a module can not be found
    """
    __slots__ = 'module', 'err_dct',

    def __init__(self, module, errors_dict):
        self.module = module
        self.err_dct = errors_dict
        super(ModuleVersionNotFound, self).__init__()

    def __str__(self):
        msg = "Unable to get version for module %s. Results:\n" % self.module
        for module, err_dct in self.err_dct.items():
            msg += " - Results for module %s:\n" % module
            for strategy, err in err_dct.items():
                msg += "   - %s: %s\n" % (get_strategy_name(strategy), err)
        return msg


class InvalidVersionFound(Exception):
    """
    Error created by get_module_version when a versiongetter returns None instead of a valid version
    """
    __slots__ = 'version',

    def __init__(self, version):
        self.version = version

    def __str__(self):
        return "Invalid version number: %s" % self.version


def get_strategy_name(strategy):
    # for now all strategies are callables: easy.
    return strategy.__name__


@lru_cache(maxsize=100)
def get_module_version_attr(module  # type: ModuleType
                            ):
    # type: (...) -> str
    """
    Simply return the __version__ attribute as recommended by PEP396
    See https://www.python.org/dev/peps/pep-0396/#specification

    Note that even if some packages use custom attribute names such as 'version' (without underscores) it does not
    seem a good idea to try them. Indeed we would have no guarantee that the semantic meaning is the same.
    See https://stackoverflow.com/questions/31146153/get-python-tornado-version/31146188.

    :param module:
    :return:
    """
    return module.__version__


# def get_version_using_importlib_metadata(module  # type: ModuleType
#                                          ):
#     # type: (...) -> str
#     """
#     Uses the importlib_metadata backport to read the version.
#     See https://importlib-metadata.readthedocs.io/en/latest/using.html#overview
#
#     Note: unfortunately this provides very bad answers in some cases (e.g. when the module is built-in)
#     so we have to protect against them
#
#     :param module:
#     :return:
#     """
#     # CAN RETURN SOMETHING CRAZY (the version of another distribution!)
#     # return version(module.__name__)
#
#     # WORKAROUND: proceed carefully and protect against crazy answers
#     from importlib_metadata import distribution
#     dist = distribution(module.__name__)
#
#     # we have to do this sanity check
#     if dist.metadata['Name'] == module.__name__:
#         return dist.version


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


def get_version_using_pkgresources(module  # type: ModuleType
                                   ):
    # type: (...) -> str
    """
    Gets the version from the package info using `pkg_resources` (from `setuptools`)
    This works even for packages installed with `pip install -e`

    Note: this is probably PEP345 https://www.python.org/dev/peps/pep-0345/

    In case there is an old local `.egg-info` in the package folder, this method may return the wrong version
    number. For this reason an error is raised in that case.

    raises: `DistributionNotFound` if the module has not been even locally installed with "pip install ."
    for example if the module has been added to the sys.path (typically in IDEs such as PyCharm)

    :param module:
    :return:
    """
    # this is part of setuptools
    from pkg_resources import working_set, Requirement, get_distribution  # get_distribution require, Distribution

    # First get the distribution

    # NO WAY ! `require` will fail in case of locally installed dependencies version conflict, which happens often
    # pkg_dist = require(pkg.__name__)[0]

    # WORKS BUT SLOW WHEN NOT FOUND because it ends up calling 'require'
    # pkg_dist = get_distribution(module.__name__)  # module.__name

    # MUCH FASTER !!!
    pkg_dist = working_set.find(Requirement.parse(module.__name__))

    # DOES NOT WORK
    # pkg_dist = get_provider(module.__name__)

    # DOES NOT WORK
    # pkg_dist = Distribution.from_filename(module.__file__)

    if pkg_dist is not None:
        # PROTECTION: if there is an old egg-info in the folder, the version will be that one, even if not installed!
        if exists(join(pkg_dist.location, module.__name__ + ".egg-info")):
            raise Exception("There is a '%s' folder in the package location so it seems to be a source project "
                            "that is not pip-installed. pkg_resources will therefore be ignored "
                            "to find the version" % (module.__name__ + ".egg-info"))

        # Finally return the version number
        return pkg_dist.version


def get_version_using_setuptools_scm(module  # type: ModuleType
                                     ):  # type: (...) -> str
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


_STRATEGIES_SUBMODULES = (get_module_version_attr,)

_STRATEGIES_ROOTMODULES = (get_version_using_pkgresources,
                           get_builtin_module_version,  # not first because another package with same name can be installed
                           # get_version_using_importlib_metadata,  # TODO useful at all ?
                           get_unzipped_wheel_or_egg_version,
                           get_version_using_setuptools_scm,
                           )


def get_module_version(module,                                        # type: ModuleType
                       submodule_strategies=_STRATEGIES_SUBMODULES,   # type: Iterable[Callable[[ModuleType], str]]
                       rootmodule_strategies=_STRATEGIES_ROOTMODULES  # type: Iterable[Callable[[ModuleType], str]]
                       ):
    # type: (...) -> str
    """
    Helper method to get the version of module `module`.

    The following techniques are tried:
     - detect explicit __version__ tag on parent package
     - try to get the version from the package info using distutils (this works even for pip install -e .)
     - Try to get version from the source directory using setuptools_scm

    :param module:
    :param submodule_strategies:
    :param rootmodule_strategies:
    :return:
    """
    all_errors = OrderedDict()

    module_name = module.__name__
    next_split_idx = module_name.rfind('.')
    is_root_module = next_split_idx < 0

    # loop until we have no parent anymore
    while module is not None:

        # init error dict for this submodule
        errors = OrderedDict()
        all_errors[module_name] = errors

        # for all strategies apply them and log the error. First valid result is returned
        if is_root_module:
            strategies = chain(submodule_strategies, rootmodule_strategies)
        else:
            strategies = submodule_strategies

        for strategy in strategies:
            try:
                # apply strategy
                version_str = strategy(module)
                # assert version valid
                if version_str is None or not isinstance(version_str, str):
                    raise InvalidVersionFound(version_str)
                else:
                    return version_str

            except Exception as e:
                # log the error
                errors[strategy] = e

        if is_root_module:
            module = None
            break
        else:
            # find parent package
            module_name = module_name[:next_split_idx]
            next_split_idx = module_name.rfind('.')
            is_root_module = next_split_idx < 0
            module = sys.modules[module_name]

    # finally return
    raise ModuleVersionNotFound(module, errors_dict=all_errors)
