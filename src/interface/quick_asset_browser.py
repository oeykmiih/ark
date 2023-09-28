# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import bl_ui

import utils
addon = utils.bpy.Addon()

from . import enums

# NOTE: keep name in sync with headers.ARK_OT_QuickEditorType
class ARK_OT_CloseAssetBrowser(bpy.types.Operator):
    bl_idname = f"{addon.name}.close_asset_browser"
    bl_label = ""
    bl_description = "Closes the current Asset Browser"

    def execute(self, context):
        session = addon.session
        session.library = bpy.context.space_data.params.asset_library_ref
        bpy.ops.screen.area_close()
        session.is_open = False
        return {"FINISHED"}

# NOTE: keep name in sync with headers.ARK_OT_QuickEditorType
class ARK_OT_QuickAssetBrowser(bpy.types.Operator):
    bl_idname = f"{addon.name}.quick_asset_browser"
    bl_label = ""
    bl_options = {'INTERNAL'}

    def execute(self, context):
        preferences = addon.preferences
        session = addon.session

        split_direction = 'VERTICAL'
        split_factor = preferences.split_factor

        if not session.is_open:
            bpy.ops.screen.area_split(direction=split_direction,factor=split_factor)
            area1 = context.area
            area2 = context.screen.areas[-1]

            _area = area1 if split_factor > 0.5 else area2
            with context.temp_override(area=_area):
                context.area.ui_type = 'ASSETS'
                context.space_data.show_region_toolbar = False
            session.is_open = True
            bpy.app.timers.register(self.set_asset_browser_defaults, first_interval=.005)
        else:
            for area in reversed(context.screen.areas):
                if area.ui_type == 'ASSETS':
                    area2 = area
                    break
                continue
            else:
                session.is_open = False
                return {'INTERFACE'}

            with context.temp_override(area=area2):
                bpy.ops.screen.area_close()
            session.is_open =  False
        return {"INTERFACE"}

    @staticmethod
    def set_asset_browser_defaults():
        preferences = addon.preferences
        session = addon.session

        area = bpy.context.screen.areas[-1]
        if area.ui_type == 'ASSETS':
            with bpy.context.temp_override(area=area):
                if session.library:
                    bpy.context.space_data.params.asset_library_ref = session.library
                else:
                    bpy.context.space_data.params.asset_library_ref = preferences.library

                match session.context:
                    case 'VIEW_3D':
                        for attribute,value in enums.EDITOR_MODE[area.ui_type]['MODELS'].items():
                                utils.rsetattr(bpy, attribute, value)
                    case 'ShaderNodeTree':
                        for attribute,value in enums.EDITOR_MODE[area.ui_type]['MATERIAL'].items():
                                utils.rsetattr(bpy, attribute, value)
        return None

@addon.property
class ARK_WindowManager_Interface_QuickAssetBrowser(bpy.types.PropertyGroup):
    context : bpy.props.StringProperty()
    library : bpy.props.StringProperty()
    is_open : bpy.props.BoolProperty()

@addon.property
class ARK_Preferences_Interface_QuickAssetBrowser(bpy.types.PropertyGroup):
    def get_libraries(self, context):
        # NOTE: Use Blender built-in libraries aswell.
        items = [
            ('ALL', "All", ""),
            ('LOCAL', "Local", ""),
            ('ESSENTIALS', "Essentials", ""),
        ]

        for lib in bpy.context.preferences.filepaths.asset_libraries.keys():
            items.append((lib, lib, ""))
        return items

    library : bpy.props.EnumProperty(
        name = "Default Library",
        items = get_libraries,
        default = None,
    )

    split_factor : bpy.props.FloatProperty(
        name = "Split Factor",
        default = 0.35,
    )

def Preferences_UI(preferences, layout):
    layout.prop(preferences, "library")
    split = layout.row(align=True).split(factor=0.245)
    split.label(text="Split Factor")
    split.prop(preferences, "split_factor", text="")
    return None

CLASSES = [
    ARK_OT_CloseAssetBrowser,
    ARK_OT_QuickAssetBrowser,
    ARK_Preferences_Interface_QuickAssetBrowser,
    ARK_WindowManager_Interface_QuickAssetBrowser,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
