# from importlib import import_module
#
# from warnings import warn
#
# from typing import Dict
#
#
# def get_module_name_from_cls(cls):
#     """
#     Returns the module name from a class.
#
#     :param cls:
#     :return:
#     """
#     mod = cls.__module__
#     if mod == '__main__':
#         mod = None
#         warn("class {0:} seems to have been defined in the main file; unfortunately this means that it's module/import"
#              " path is unknown, so you might have to provide `cls_lookup_map` when decoding".format(cls))
#     return mod
#
#
# def get_cls_from_instance_type(mod, name, cls_lookup_map: Dict = None):
#     """
#     Returns a class from a module and class name. If the module is None, the
#
#     :param mod:
#     :param name:
#     :param cls_lookup_map:
#     :return:
#     """
#     cls_lookup_map = cls_lookup_map or dict()
#
#     cls = None
#     if mod is not None:
#         imp_err = None
#
#         try:
#             # First try to import the module
#             # module_ = __import__(module_name)  this was not importing correctly
#             module = import_module('{0:}'.format(mod, name))
#         except ImportError as err:
#             imp_err = 'encountered import error "{0:}" while importing "{1:}" to decode a json file; perhaps ' \
#                       'it was encoded in a different environment where {1:}.{2:} was available'.format(err, mod, name)
#         else:
#             # Then try to find the class in the module
#             if hasattr(module, name):
#                 cls = getattr(module, name)
#             else:
#                 imp_err = 'imported "{0:}" but could find "{1:}" inside while decoding a json file (found {2:}' \
#                           ''.format(module, name, ', '.join(attr for attr in dir(module) if not attr.startswith('_')))
#
#         # Handle errors
#         if imp_err:
#             if name in cls_lookup_map:
#                 cls = cls_lookup_map[name]
#             else:
#                 raise ImportError(imp_err)
#
#     else:
#         try:
#             # Try to import from main
#             cls = getattr((__import__('__main__')), name)
#
#         except (ImportError, AttributeError):
#             if name not in cls_lookup_map:
#                 raise ImportError('class {0:s} seems to have been exported from the main file, which means it has no '
#                                   'module/import path set; you need to provide cls_lookup_map which maps names '
#                                   'to classes'.format(name))
#             cls = cls_lookup_map[name]
#
#     return cls
