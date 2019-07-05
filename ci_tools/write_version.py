#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

import click
from setuptools_scm import get_version


@click.command()
@click.argument('pkg_name')
def write_version(pkg_name):
    file_name = '%s/_version.py' % pkg_name
    print("Writing version to file: %s" % file_name)
    get_version('.', write_to=file_name)


if __name__ == '__main__':
    write_version()
