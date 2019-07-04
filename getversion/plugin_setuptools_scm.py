from os.path import dirname


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
