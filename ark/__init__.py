# SPDX-License-Identifier: GPL-2.0-or-later
bl_info = {
    "name" : "ARK",
    "author" : "joao@kyeo.xyz",
    "description" : "",
    "wiki_url": "",
    "blender" : (3, 3, 0),
    "version" : (0, 4, 1),
    "category" : "",
    "location" : "",
    "warning" : "",
}

__version__ = "0.4.1-dev"
__prefix__ = "ARK"

from ark import utils
addon = utils.bpy.Addon()

MODULES = {
    "cameras" : None,
    "interface" : None,
    "materials" : None,
    "worlds" : None,
    "presets" : None,
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

# Note: Registering PROPS classes need their child PROPS to be already registered.
##  Unregistering MODULES might depend on a registered PROP,
## thus we got to keep PROPS until all child MODULES are unregistered.

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(PROPS)
    addon.set_properties(PROPS)
    return None

def unregister():
    utils.bpy.unregister_modules(MODULES)
    utils.bpy.unregister_classes(PROPS)
    utils.cleanse_globals()
    return None
