# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from ark import utils
addon = utils.bpy.Addon()

MODULES = {
    "catalog" : None,
    "groups" : None,
}
MODULES = utils.import_modules(MODULES)

@addon.property
class WindowManager_Materials(bpy.types.PropertyGroup):
    pass

@addon.property
class Preferences_Materials(bpy.types.PropertyGroup):
    pass

def UI(preferences, layout):
    items = (name for name, module in MODULES.items() if hasattr(module, "UI"))
    for name in items:
        module = MODULES[name]
        properties = getattr(preferences, name)
        layout = layout.box()
        module.UI(properties, layout)
    return None

CLASSES = [
    WindowManager_Materials,
    Preferences_Materials,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_modules(MODULES)
    utils.bpy.unregister_classes(CLASSES)
    return None
