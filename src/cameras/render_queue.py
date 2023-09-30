# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

import utils
addon = utils.bpy.Addon()

@addon.property
class ARK_WindowManager_Cameras_RenderQueue(bpy.types.PropertyGroup):
    pass

@addon.property
class ARK_Preferences_Cameras_RenderQueue(bpy.types.PropertyGroup):
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
    ARK_WindowManager_Cameras_RenderQueue,
    ARK_Preferences_Cameras_RenderQueue,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    utils.bpy.unregister_modules(MODULES)
    return None
