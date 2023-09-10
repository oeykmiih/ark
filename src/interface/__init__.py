# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

class ARK_PROPS_WindowManager_Interface(bpy.types.PropertyGroup):
    pass

class ARK_PREFS_Interface(bpy.types.PropertyGroup):
    pass

def ARK_PREFS_Interface_UI(preferences, layout):
    box = layout.box()
    return None

CLASSES = [
    ARK_PROPS_WindowManager_Interface,
    ARK_PREFS_Interface,
]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    return None

def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    return None
