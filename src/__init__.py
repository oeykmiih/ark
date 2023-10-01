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
__prefix__ = "ARK"

def import_libraries(libraries):
    import os
    import site
    import sys
    import importlib

    LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "libs"))
    try:
        if os.path.isdir(LIB_DIR) and LIB_DIR not in sys.path:
            sys.path.insert(0, LIB_DIR)
        for name, module in libraries.items():
            libraries[name] = importlib.import_module(name)
        globals().update(libraries)
    finally:
        if LIB_DIR in sys.path:
            sys.path.remove(LIB_DIR)
    return None


LIBRARIES = {
    "utils" : None,
}
import_libraries(LIBRARIES)
addon = utils.bpy.Addon()

MODULES = {
    "cameras" : None,
    "materials" : None,
    "interface" : None,
}
MODULES = utils.import_modules(MODULES)
import bpy

@addon.property
class Preferences(bpy.types.AddonPreferences):
    bl_idname = addon.name

    items = (name for name, module in MODULES.items() if hasattr(module, "UI"))

    ui_prefs_tab: bpy.props.EnumProperty(
        name = "ui_prefs_tab",
        description = "",
        items = utils.bpy.enum_from_list(items, raw=True),
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.row().prop(self, "ui_prefs_tab", expand=True)
        properties = getattr(self, self.ui_prefs_tab)
        MODULES[self.ui_prefs_tab].UI(properties, layout)
        return None

@addon.property
class WindowManager(bpy.types.PropertyGroup):
    pass

@addon.property
class Scene(bpy.types.PropertyGroup):
    pass

PROPS = [
    Preferences,
    WindowManager,
    Scene,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(PROPS)
    addon.set_properties(PROPS)
    return None

def unregister():
    utils.bpy.unregister_classes(PROPS)
    utils.bpy.unregister_modules(MODULES)
    utils.cleanse_globals(LIBRARIES)
    return None
