# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import bl_ui
import json

from ark import utils
addon = utils.bpy.Addon()

from . import enums

# NOTE: keep name in sync with interface.headers
class ARK_OT_SetEditorMode(bpy.types.Operator):
    """Changes editor type for this area."""
    bl_idname = f"{addon.name}.set_editor_mode"
    bl_label = "Set Editor Mode"
    bl_options = {'INTERNAL'}

    ui_type : bpy.props.StringProperty(
        name = "",
        description = "",
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

        for ui_type in enums.EDITOR_TYPE:
            pie_count += 1
            # NOTE: This is legacy code to handle proper layout, keeping it if pie menu count goes down again
            ##         4
            ##     5       6
            ## 1              2
            ##     7       8
            ##         3
            # while pie_count in [4,]:
            #     layout.separator()
            #     pie_count += 1

            operator = layout.operator(
                f"{addon.name}.set_editor_mode",
                icon = enums.EDITOR_TYPE_ICONS[ui_type]
            )
            operator.ui_type = ui_type
        return None

# NOTE: keep name in sync with hide.HEADERS
class ARK_OT_QuickEditorType(bpy.types.Operator):
    """Changes editor type for this area."""
    bl_idname = f"{addon.name}.quick_editor_type"
    bl_label = "Quick Editor Type"
    bl_options = {'INTERNAL'}

    shift : bpy.props.BoolProperty()
    ctrl : bpy.props.BoolProperty()

    ui_type : bpy.props.StringProperty(
        name = "",
        description = "",
        default = 'VIEW_3D',
    )

    def invoke(self, context, event):
        self.shift = event.shift
        self.ctrl = event.ctrl
        return self.execute(context)

    def execute(self, context):
        if self.shift and self.ctrl:
            bpy.ops.wm.call_menu_pie(name=ARK_MT_PIE_SetEditorMode.__name__)
        elif self.shift:
            if context.area.ui_type in ['OUTLINER', 'PROPERTIES']:
                bpy.ops.ark.quick_editor_split()
            else:
                bpy.ops.ark.quick_asset_browser()
        elif self.ctrl:
            bpy.ops.ark.quick_editor_split()
        else:
            context.area.ui_type = self.ui_type
        return {'INTERFACE'}

class ARK_OT_QuickEditorSplit(bpy.types.Operator):
    bl_idname = f"{addon.name}.quick_editor_split"
    bl_label = ""
    bl_options = {'INTERNAL'}

    ui_type : bpy.props.StringProperty(
        name = "",
        description = "",
        default = 'VIEW_3D',
    )

    def execute(self, context):
        preferences = addon.preferences
        session = addon.session

        if not session.is_open:
            area1 = context.area

            match area1.ui_type:
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

            bpy.ops.screen.area_split(direction=split_direction,factor=split_factor)
            area2 = context.screen.areas[-1]

            _area = area1 if split_factor > 0.5 else area2
            with context.temp_override(area=_area):
                context.area.ui_type = self.ui_type
            session.is_open = True
            session.area2 = str(_area)
        else:
            for area in reversed(context.screen.areas):
                if str(area) == session.area2:
                    area2 = area
                    break
                continue
            else:
                session.is_open = False
                return {'INTERFACE'}

            with context.temp_override(area=area2):
                bpy.ops.screen.area_close()
            session.is_open = False
        return {'INTERFACE'}

@addon.property
class WindowManager_Interface_QuickEditor(bpy.types.PropertyGroup):
    is_open : bpy.props.BoolProperty()
    area2 : bpy.props.StringProperty()

@addon.property
class Preferences_Interface_QuickEditor(bpy.types.PropertyGroup):
    split_factor : bpy.props.FloatProperty(
        name = "Split Factor",
        default = 0.60,
    )

def UI(preferences, layout):
    split = layout.row(align=True).split(factor=0.245)
    split.label(text="Split Factor")
    split.prop(preferences, "split_factor", text="")
    return None

CLASSES = [
    ARK_OT_QuickEditorType,
    ARK_OT_SetEditorMode,
    ARK_MT_PIE_SetEditorMode,
    ARK_OT_QuickEditorSplit,
    Preferences_Interface_QuickEditor,
    WindowManager_Interface_QuickEditor,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
