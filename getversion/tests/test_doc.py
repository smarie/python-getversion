#  Authors: Sylvain Marie <sylvain.marie@se.com>
#
#  License: BSD 3 clause

from getversion import get_module_version


def test_doc_imported(capsys):
    # Get the version of an imported module
    from xml import dom
    version, details = get_module_version(dom)

    with capsys.disabled():
        print(version)
        print(details)

    print(version)
    print(details)

    out, err = capsys.readouterr()

    assert out == """3.7.3.final.0
Version '3.7.3.final.0' found for module 'xml.dom' by strategy 'get_builtin_module_version', after the following failed attempts:
 - Attempts for module 'xml.dom':
   - <get_module_version_attr>: module 'xml.dom' has no attribute '__version__'
 - Attempts for module 'xml':
   - <get_module_version_attr>: module 'xml' has no attribute '__version__'
   - <get_version_using_pkgresources>: Invalid version number: None
   - <get_builtin_module_version>: SUCCESS: 3.7.3.final.0

"""
