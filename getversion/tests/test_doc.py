#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

import sys

from getversion import get_module_version


python_sys_version = sys_version = '.'.join([str(v) for v in sys.version_info])


def test_doc_imported(capsys):
    # Get the version of an imported module
    from xml import dom
    version, details = get_module_version(dom)

    with capsys.disabled():
        print(version)
        print(details)

    print(version)
    print(details)

    if sys.version_info > (3, 0):
        first = "module 'xml.dom'"
        second = "module 'xml'"
    else:
        first = "'module' object"
        second = "'module' object"

    out, err = capsys.readouterr()

    assert out == """{sysversion}
Version '{sysversion}' found for module 'xml.dom' by strategy 'get_builtin_module_version', after the following failed attempts:
 - Attempts for module 'xml.dom':
   - <get_module_version_attr>: {first} has no attribute '__version__'
 - Attempts for module 'xml':
   - <get_module_version_attr>: {second} has no attribute '__version__'
   - <get_version_using_pkgresources>: Invalid version number: None
   - <get_builtin_module_version>: SUCCESS: {sysversion}

""".format(sysversion=python_sys_version, first=first, second=second)
