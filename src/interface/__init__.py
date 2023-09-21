# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

import utils
addon = utils.bpy.Addon()

MODULES = {
    "headers" : None,
    "quickassetbrowser" : None,
}
MODULES = utils.import_modules(MODULES)

class ARK_OT_ToogleInterface(bpy.types.Operator):
    pass

@addon.property
class ARK_WindowManager_Interface(bpy.types.PropertyGroup):
    pass

@addon.property
class ARK_Preferences_Interface(bpy.types.PropertyGroup):
    pass

def Preferences_UI(preferences, layout):
    items = (name for name, module in MODULES.items() if hasattr(module, "Preferences_UI"))
    for name in items:
        module = MODULES[name]
        properties = getattr(preferences, name)
        layout = layout.box()
        module.Preferences_UI(properties, layout)
    return None

    # box = layout.box()
    box.prop(preferences.interface, "assets_library_default")
    split = box.row(align=True).split(factor=0.35)
    split.label(text="QuickAssetBrowser Factor")
    split.prop(preferences.interface, "assets_split_factor", text="")
    # return None

CLASSES = [
    ARK_WindowManager_Interface,
    ARK_Preferences_Interface,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    utils.bpy.unregister_modules(MODULES)
    return None
