# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import bl_ui

from ark import utils
addon = utils.bpy.Addon()

from . import enums
from . import quick_editor

# NOTE: keep name in sync with headers.ARK_OT_QuickEditorType
class ARK_OT_CloseAssetBrowser(bpy.types.Operator):
    bl_idname = f"{addon.name}.close_asset_browser"
    bl_label = ""
    bl_description = "Closes the current Asset Browser"

    shift : bpy.props.BoolProperty()
    ctrl : bpy.props.BoolProperty()

    def invoke(self, context, event):
        self.shift = event.shift
        self.ctrl = event.ctrl
        return self.execute(context)

    def execute(self, context):
        if self.shift and self.ctrl:
            bpy.ops.wm.call_menu_pie(name=quick_editor.ARK_MT_PIE_SetEditorMode.__name__)
        else:
            session = addon.session
            session.library = context.space_data.params.asset_library_reference
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
            session.context = context.area.ui_type
            session.area2 = str(_area)
            bpy.app.timers.register(self.set_asset_browser_defaults, first_interval=.005)
        else:
            for area in reversed(context.screen.areas):
                if str(area) == session.area2:
                    area2 = area
                    break
            else:
                session.is_open = False
                return {'INTERFACE'}

            with context.temp_override(area=area2):
                bpy.ops.screen.area_close()
            session.is_open = False
        return {"INTERFACE"}

    @staticmethod
    def set_asset_browser_defaults():
        preferences = addon.preferences
        session = addon.session
        context = bpy.context

        area = context.screen.areas[-1]
        if area.ui_type == 'ASSETS':
            with context.temp_override(area=area):
                if session.library:
                    context.space_data.params.asset_library_reference = session.library
                else:
                    context.space_data.params.asset_library_reference = preferences.library

                match session.context:
                    case 'VIEW_3D':
                        for attribute,value in enums.EDITOR_MODE[area.ui_type]['MODELS'].items():
                                utils.rsetattr(bpy, attribute, value)
                    case 'ShaderNodeTree':
                        for attribute,value in enums.EDITOR_MODE[area.ui_type]['MATERIAL'].items():
                                utils.rsetattr(bpy, attribute, value)
        return None

@addon.property
class WindowManager_Interface_QuickAssetBrowser(bpy.types.PropertyGroup):
    context : bpy.props.StringProperty()
    library : bpy.props.StringProperty()
    is_open : bpy.props.BoolProperty()
    area2 : bpy.props.StringProperty()

@addon.property
class Preferences_Interface_QuickAssetBrowser(bpy.types.PropertyGroup):
    def get_libraries(self, context):
        # NOTE: Use Blender built-in libraries aswell.
        items = [
            ('ALL', "All", ""),
            ('LOCAL', "Local", ""),
            ('ESSENTIALS', "Essentials", ""),
        ]

        for lib in context.preferences.filepaths.asset_libraries.keys():
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

def UI(preferences, layout):
    layout.prop(preferences, "library")
    split = layout.row(align=True).split(factor=0.245)
    split.label(text="Split Factor")
    split.prop(preferences, "split_factor", text="")
    return None

CLASSES = [
    ARK_OT_CloseAssetBrowser,
    ARK_OT_QuickAssetBrowser,
    WindowManager_Interface_QuickAssetBrowser,
    Preferences_Interface_QuickAssetBrowser,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
