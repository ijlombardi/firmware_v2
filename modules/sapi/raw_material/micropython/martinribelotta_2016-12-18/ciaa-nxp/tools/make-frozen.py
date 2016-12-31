#!/usr/bin/env python
#
# Create frozen modules structure for MicroPython.
#
# Usage:
#
# Have a directory with modules to be frozen (only modules, not packages
# supported so far):
#
# frozen/foo.py
# frozen/bar.py
#
# Run script, passing path to the directory above:
#
# ./make-frozen.py frozen > frozen.c
#
# Include frozen.c in your build, having defined MICROPY_MODULE_FROZEN in
# config.
#
# 2016. Changes:
#   File extension filter. Only ".py" and ".PY" files are read.
#
from __future__ import print_function
import sys
import os


def module_name(f):
    return f[:-len(".py")]

modules = []

root = sys.argv[1].rstrip("/")
root_len = len(root)

flagIncludeTests = os.environ.has_key("MP_INCLUDE_TESTS")

for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        if f.endswith( ('.py','.PY') ):
            fullpath = dirpath + "/" + f
            if flagIncludeTests==False and dirpath==root+"/testing":
                continue #skip test classes if MP_INCLUDE_TESTS is not defined
            st = os.stat(fullpath)
            modules.append((fullpath[root_len + 1:], st))


print("#include <stdint.h>")
print("const char mp_frozen_names[] = {")
for f, st in modules:
    m = module_name(f.replace("/","_"))
    print('"%s\\0"' % m)
print('"\\0"};')

print("const uint32_t mp_frozen_sizes[] = {")

for f, st in modules:
    print("%d," % st.st_size)

print("};")

print("const char mp_frozen_content[] = {")
for f, st in modules:
    data = open(sys.argv[1] + "/" + f, "rb").read()
    # Python2 vs Python3 tricks
    data = repr(data)
    if data[0] == "b":
        data = data[1:]
    data = data[1:-1]
    data = data.replace('"', '\\"')
    print('"%s\\0"' % data)
print("};")
