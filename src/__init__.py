# SPDX-License-Identifier: GPL-2.0-or-later
bl_info = {
    "name" : "ARK",
    "author" : "joao@kyeo.xyz",
    "description" : "",
    "wiki_url": "",
    "blender" : (3, 3, 0),
    "version" : (0, 0, 0),
    "category" : "",
    "location" : "",
    "warning" : "",
}

__version__ = "0.1.0"
__name__ = "ark"
__prefix__ = "ARK"

import importlib
import os
import site
import sys


LIBRARIES = [
]

if LIBRARIES:
    LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "libs"))
    try:
        if os.path.isdir(LIB_DIR) and LIB_DIR not in sys.path:
            sys.path.insert(0, LIB_DIR)
        for name in LIBRARIES:
            if name not in locals():
                importlib.import_module(name)
            else:
                importlib.reload(name)
    finally:
        if LIB_DIR in sys.path:
            sys.path.remove(LIB_DIR)

FEATURES = {
    "cameras" : None,
    "materials" : None,
}
MODULES = {}
MODULES["utils"] = None
MODULES.update(FEATURES)
MODULES["properties"] = None

if "bpy" in locals():
    for name, module in MODULES.items():
        MODULES[name] = importlib.reload(f"{__package__}.{name}")
else:
    for name, module in MODULES.items():
        MODULES[name] = importlib.import_module(f"{__package__}.{name}")

import bpy
# NOTE: Only import bpy after modules to allow it to reload.

def cleanse_modules():
    """Remove all plugin modules from sys.modules, will load them again, creating an effective hit-reload soluton"""
    # https://devtalk.blender.org/t/plugin-hot-reload-by-cleaning-sys-modules/20040

    import sys
    all_modules = sys.modules
    all_modules = dict(sorted(all_modules.items(),key= lambda x:x[0])) #sort them

    for key in all_modules.keys():
        if key.startswith(__name__):
            del sys.modules[key]
    return None

def register():
    for module in MODULES.values():
        module.register()
    return None

def unregister():
    for module in reversed(MODULES.values()):
        module.unregister()
    cleanse_modules()
    return None
