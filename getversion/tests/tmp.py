from stdlib_list import stdlib_list
import sys

all_stdlib_symbols = stdlib_list('.'.join([str(v) for v in sys.version_info[0:2]]))

module_name = 'collections'

if module_name in all_stdlib_symbols:
    print("%s is in stdlib" % module_name)