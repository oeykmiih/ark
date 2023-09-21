# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

import utils
addon = utils.bpy.Addon()

MODULES = {
    "catalog" : None,
}
MODULES = utils.import_modules(MODULES)

@addon.property
class ARK_WindowManager_Materials(bpy.types.PropertyGroup):
    pass

@addon.property
class ARK_Preferences_Materials(bpy.types.PropertyGroup):
    pass

def Preferences_UI(preferences, layout):
    items = (name for name, module in MODULES.items() if hasattr(module, "Preferences_UI"))
    for name in items:
        module = MODULES[name]
        properties = getattr(preferences, name)
        layout = layout.box()
        module.Preferences_UI(properties, layout)
    return None

CLASSES = [
    ARK_WindowManager_Materials,
    ARK_Preferences_Materials,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    utils.bpy.unregister_modules(MODULES)
    return None
