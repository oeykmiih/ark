# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import bl_ui
import json

import utils
addon = utils.bpy.Addon()

from . import enums

# NOTE: keep name in sync with hide.HEADERS
class ARK_OT_SetEditorMode(bpy.types.Operator):
    bl_idname = f"{addon.name}.set_editor_mode"
    bl_label = ""
    bl_options = {'INTERNAL'}

    ui_type : bpy.props.EnumProperty(
        name = "",
        description = "",
        items = enums.EDITOR_TYPE,
        default = 'VIEW_3D',
    )

    ui_mode : bpy.props.StringProperty(
        name = "",
        description = "",
        default = 'NONE',
    )

    def execute(self, context):
        context.area.ui_type = self.ui_type
        if self.ui_mode != 'NONE':
            for attribute, value in enums.EDITOR_MODE[self.ui_type][self.ui_mode].items():
                utils.rsetattr(bpy, attribute, value)
        return {'INTERFACE'}

class ARK_MT_PIE_SetEditorMode(bpy.types.Menu):
    bl_label = ""

    def draw(self, context):
        layout = self.layout.menu_pie()

        session = addon.session
        pie_count = 0

        for ui_type, children in enums.EDITOR_MODE.items():
            pie_count += 1
            while pie_count in [4, 7, 8]:
                layout.separator()
                pie_count += 1

            operator = layout.operator(
                f"{addon.name}.set_editor_mode",
                icon = enums.EDITOR_TYPE_ICONS[ui_type]
            )
            operator.ui_type = ui_type
        return None

# NOTE: keep name in sync with hide.HEADERS
class ARK_OT_QuickEditorType(bpy.types.Operator):
    bl_idname = f"{addon.name}.quick_editor_type"
    bl_label = ""
    bl_options = {'INTERNAL'}

    shift : bpy.props.BoolProperty()
    ctrl : bpy.props.BoolProperty()

    ui_type : bpy.props.EnumProperty(
        name = "",
        description = "",
        items = enums.EDITOR_TYPE,
        default = 'VIEW_3D',
    )

    def invoke(self, context, event):
        self.shift = event.shift
        self.ctrl = event.ctrl
        return self.execute(context)

    def execute(self, context):
        if context.area.ui_type == 'ASSETS' and not self.shift:
            bpy.ops.ark.close_asset_browser()
            return {'INTERFACE'}

        if self.shift and self.ctrl:
            bpy.ops.ark.quick_editor_split()
        elif self.shift:
            bpy.ops.wm.call_menu_pie(name=ARK_MT_PIE_SetEditorMode.__name__)
        elif self.ctrl:
            bpy.ops.ark.quick_asset_browser()
        else:
            context.area.ui_type = self.ui_type
        return {'INTERFACE'}

class ARK_OT_QuickEditorSplit(bpy.types.Operator):
    bl_idname = f"{addon.name}.quick_editor_split"
    bl_label = ""
    bl_options = {'INTERNAL'}

    ui_type : bpy.props.EnumProperty(
        name = "",
        description = "",
        items = enums.EDITOR_TYPE,
        default = 'VIEW_3D',
    )

    def execute(self, context):
        preferences = addon.preferences
        session = addon.session

        if not session.open:
            match context.area.ui_type:
                case 'VIEW_3D':
                    self.ui_type = 'ShaderNodeTree'
                case 'ShaderNodeTree':
                    self.ui_type = 'VIEW_3D'
                case 'OUTLINER':
                    self.ui_type = 'PROPERTIES'
                case 'PROPERTIES':
                    self.ui_type = 'OUTLINER'
                case _:
                    return {'INTERFACE'}

            split_direction = 'HORIZONTAL'
            split_factor = preferences.split_factor

            areas = []
            scheme = []
            # Load all areas into list
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    areas.append(area)
                    scheme.append(area.ui_type)

            session.prev_scheme = json.dumps(scheme)

            # Split current area
            bpy.ops.screen.area_split(direction=split_direction,factor=split_factor)

            # Look for area not in list and override context
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area not in areas:
                        with context.temp_override(area=area):
                            context.area.ui_type = self.ui_type
                        break
            session.open = True
        else:
            prev_scheme = json.loads(session.prev_scheme)
            session.prev_scheme = ""
            areas = []
            curr_scheme = []
            # Load all areas into list
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    areas.append(area)
                    curr_scheme.append(area.ui_type)

            if len(curr_scheme) > len(prev_scheme):
                currscheme, prev_scheme = utils.std.pad_lists(curr_scheme, prev_scheme)
                for index, area in enumerate(areas):
                    if curr_scheme[index] != prev_scheme[index]:
                        with context.temp_override(area=areas[index]):
                            bpy.ops.screen.area_close()
                        break
            session.open = False
        return {'INTERFACE'}

@addon.property
class ARK_WindowManager_Interface_QuickEditor(bpy.types.PropertyGroup):
    open : bpy.props.BoolProperty(
        name = "ARK_OT_QuickEditorSplit.open",
        default = False,
    )

    prev_scheme : bpy.props.StringProperty(
        name = "ARK_OT_QuickEditorSplit.scheme"
    )

@addon.property
class ARK_Preferences_Interface_QuickEditor(bpy.types.PropertyGroup):
    split_factor : bpy.props.FloatProperty(
        name = "Split Factor",
        default = 0.45,
    )

def Preferences_UI(preferences, layout):
    split = layout.row(align=True).split(factor=0.245)
    split.label(text="Split Factor")
    split.prop(preferences, "split_factor", text="")
    return None

CLASSES = [
    ARK_OT_QuickEditorType,
    ARK_OT_SetEditorMode,
    ARK_MT_PIE_SetEditorMode,
    ARK_OT_QuickEditorSplit,
    ARK_Preferences_Interface_QuickEditor,
    ARK_WindowManager_Interface_QuickEditor,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
