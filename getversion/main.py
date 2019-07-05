#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

from collections import OrderedDict
from itertools import chain
from os.path import join, exists
import sys
from types import ModuleType

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

try:  # python 3.5+
    from typing import Union, Iterable, Callable
except ImportError:
    pass

from getversion.plugin_builtins import get_builtin_module_version
from getversion.plugin_eggs_and_wheels import get_unzipped_wheel_or_egg_version
from getversion.plugin_setuptools_scm import get_version_using_setuptools_scm


def get_strategy_name(strategy):
    # for now, all strategies are callables: easy.
    return strategy.__name__


def get_module_name(module):
    # for now we only use ModuleType modules
    return module.__name__


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

    # MUCH FASTER !!! because in case of failure it does not try to do a 'require'
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


_STRATEGIES_SUBMODULES = (get_module_version_attr,)

_STRATEGIES_ROOTMODULES = (get_version_using_pkgresources,
                           get_builtin_module_version,  # not first because another package with same name can be installed
                           # get_version_using_importlib_metadata,  # does not seem useful for now
                           get_unzipped_wheel_or_egg_version,
                           get_version_using_setuptools_scm,
                           )


def err_dct_to_str(err_dct  # Dict
                   ):
    # type: (...) -> str
    msg = ""
    for module, err_dct in err_dct.items():
        if len(err_dct) > 0:
            msg += " - Attempts for module '%s':\n" % module
            for strategy, err in err_dct.items():
                msg += "   - <%s>: %s\n" % (get_strategy_name(strategy), err)
    return msg


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
        return "Unable to get version for module '%s'. Results:\n%s" \
               % (get_module_name(self.module), err_dct_to_str(self.err_dct))


class InvalidVersionFound(Exception):
    """
    Error created by get_module_version when a versiongetter returns None instead of a valid version
    """
    __slots__ = 'version',

    def __init__(self, version):
        self.version = version

    def __str__(self):
        return "Invalid version number: %s" % self.version


class DetailedResults(object):
    """
    Returned by `get_module_version` for detailed results about which strategy failed before the winning one.
    """
    __slots__ = 'module', 'err_dct', 'winning_strategy', 'version_found'

    def __init__(self, module, err_dct, winning_strategy, version_found):
        self.module = module
        self.err_dct = err_dct
        self.winning_strategy = winning_strategy
        self.version_found = version_found

    def __str__(self):
        return "Version '%s' found for module '%s' by strategy '%s', after the following failed attempts:\n%s"\
               % (self.version_found, get_module_name(self.module), get_strategy_name(self.winning_strategy),
                  err_dct_to_str(self.err_dct))


@lru_cache(maxsize=100)
def get_module_version(module,                                        # type: ModuleType
                       submodule_strategies=_STRATEGIES_SUBMODULES,   # type: Iterable[Callable[[ModuleType], str]]
                       rootmodule_strategies=_STRATEGIES_ROOTMODULES  # type: Iterable[Callable[[ModuleType], str]]
                       ):
    # type: (...) -> Tuple[str, DetailedResults]
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
    # if isinstance(module, str) TODO support str:
    # '__main__' and '<...' (pydoc, ipython, etc.)

    all_errors = OrderedDict()

    original_module = module
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
                    errors[strategy] = "SUCCESS: %s" % version_str
                    return version_str, DetailedResults(original_module, all_errors, strategy, version_str)

            except Exception as e:
                # log the error
                errors[strategy] = e

        if is_root_module:
            del module
            break
        else:
            # find parent package
            module_name = module_name[:next_split_idx]
            next_split_idx = module_name.rfind('.')
            is_root_module = next_split_idx < 0
            module = sys.modules[module_name]

    # finally return
    raise ModuleVersionNotFound(original_module, errors_dict=all_errors)
