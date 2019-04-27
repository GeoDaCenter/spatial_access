from jinja2 import Template
import sys

if len(sys.argv) > 1:
    SRC_PATH = sys.argv[1]
else:
    SRC_PATH = "./"

EDIT_WARNING = """# WARNING: This file is automatically generated. 
# Update pyx_src/static.pyx and pyx_src/dynamic to change."""

CLASS_TYPES = [{"class_name": "transitMatrixIxI",
                "py_class_name":"pyTransitMatrixIxI",
                "row_type_full":"unsigned long int",
                "col_type_full": "unsigned long int",
                "row_type": "ulong",
                "col_type": "ulong",
                "value_type" : "ushort"},
               {"class_name": "transitMatrixIxS",
                "py_class_name": "pyTransitMatrixIxS",
                "row_type_full": "unsigned long int",
                "col_type_full": "string",
                "row_type": "ulong",
                "col_type": "string",
                "value_type": "ushort"},
               {"class_name": "transitMatrixSxI",
                "py_class_name": "pyTransitMatrixSxI",
                "row_type_full": "string",
                "col_type_full": "unsigned long int",
                "row_type": "string",
                "col_type": "ulong",
                "value_type": "ushort"},
               {"class_name": "transitMatrixSxS",
                "py_class_name": "pyTransitMatrixSxS",
                "row_type_full": "string",
                "col_type_full": "string",
                "row_type": "string",
                "col_type": "string",
                "value_type": "ushort"},
               ]

with open(SRC_PATH + '_p2pExtension.pyx', "w+") as target:

    target.write(EDIT_WARNING)

    target.write("\n\n# Static:\n\n")

    # write static files
    with open(SRC_PATH + 'pyx_src/static.pyx') as static_file:
        static_source = static_file.read()
        target.write(static_source)

    # write dynamic files
    target.write("\n\n# Dynamic Templates: \n\n")
    with open(SRC_PATH + 'pyx_src/dynamic.pyx') as dynamic_file:
        dynamic_source = dynamic_file.read()
        dynamic_template = Template(dynamic_source)
        for class_type in CLASS_TYPES:
            target.write("\n\n")
            target.write(dynamic_template.render(**class_type))