#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

def get_version_using_importlib_metadata(module  # type: ModuleType
                                         ):
    # type: (...) -> str
    """
    Uses the importlib_metadata backport to read the version.
    See https://importlib-metadata.readthedocs.io/en/latest/using.html#overview

    Note: unfortunately this provides very bad answers in some cases (e.g. when the module is built-in)
    so we have to protect against them

    :param module:
    :return:
    """
    # CAN RETURN SOMETHING CRAZY (the version of another distribution!)
    # return version(module.__name__)

    # WORKAROUND: proceed carefully and protect against crazy answers
    from importlib_metadata import distribution
    dist = distribution(module.__name__)

    # we have to do this sanity check
    if dist.metadata['Name'] == module.__name__:
        return dist.version
