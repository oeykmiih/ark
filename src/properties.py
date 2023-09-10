# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from . import addon

from . import cameras
from . import materials

class ARK_PREFS(bpy.types.AddonPreferences):
    """Store options"""
    bl_idname = addon.name

    ui_prefs_tab: bpy.props.EnumProperty(
        name = "ui_prefs_tab",
        description = "",
        items = [
            ('CAMERAS', "Cameras", ""),
            ('MATERIALS', "Materials", ""),
        ]
    )

    cameras : bpy.props.PointerProperty(type=cameras.ARK_PREFS_Cameras)
    materials : bpy.props.PointerProperty(type=materials.ARK_PREFS_Materials)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.row().prop(self, "ui_prefs_tab", expand=True)
        match self.ui_prefs_tab:
            case 'CAMERAS':
                cameras.ARK_PREFS_Cameras_UI(self, col)
            case 'MATERIALS':
                materials.ARK_PREFS_Materials_UI(self, col)
            case _:
                pass
        return None

class ARK_PROPS_WindowManager(bpy.types.PropertyGroup):
    """Store state"""
    materials : bpy.props.PointerProperty(type=materials.ARK_PROPS_WindowManager_Materials)

class ARK_PROPS_Scene(bpy.types.PropertyGroup):
    """Define Custom Properties"""
    active_camera_index: bpy.props.IntProperty(
        name="",
        default=0,
    )

CLASSES = [
    ARK_PREFS,
    ARK_PROPS_WindowManager,
    ARK_PROPS_Scene,
]

PROPS = CLASSES[1:]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    for prop in PROPS:
        addon.set_props(prop)
    return None

def unregister():
    for prop in reversed(PROPS):
        addon.del_props(prop)

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    return None
