# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from .. import addon
from .. import utils

from . import enums

class ARK_OT_QuickEditorType(bpy.types.Operator):
    """Tooltip"""
    bl_idname = f"{addon.name}.set_editor_type"
    bl_label = ""

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
        if self.shift and self.ctrl:
            pass
        elif self.shift:
            bpy.ops.wm.call_menu_pie(name=ARK_MT_PIE_SetEditorMode.__name__)
        elif self.ctrl:
            pass
        else:
            bpy.context.area.ui_type = self.ui_type
        return {'FINISHED'}

class ARK_OT_SetEditorMode(bpy.types.Operator):
    """Tooltip"""
    bl_idname = f"{addon.name}.set_editor_mode"
    bl_label = ""

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
        return {'FINISHED'}

def ARK_BT_NODE_SetEditorType(self, context):
    ui_type = 'VIEW_3D'
    operator = self.layout.operator(
        ARK_OT_QuickEditorType.bl_idname,
        text="",
        icon=enums.EDITOR_TYPE_ICONS[ui_type],
    )
    operator.ui_type = ui_type
    # self.layout.separator()
    return None

def ARK_BT_OUTLINER_SetEditorType(self, context):
    ui_type = 'PROPERTIES'
    operator = self.layout.operator(
        ARK_OT_QuickEditorType.bl_idname,
        text="",
        icon=enums.EDITOR_TYPE_ICONS[ui_type],
    )
    operator.ui_type = ui_type
    # self.layout.separator()
    return None

def ARK_BT_PROPERTIES_SetEditorType(self, context):
    ui_type = 'OUTLINER'
    operator = self.layout.operator(
        ARK_OT_QuickEditorType.bl_idname,
        text="",
        icon=enums.EDITOR_TYPE_ICONS[ui_type],
    )
    operator.ui_type = ui_type
    # self.layout.separator()
    return None

def ARK_BT_VIEW3D_SetEditorType(self, context):
    ui_type = 'ShaderNodeTree'
    operator = self.layout.operator(
        ARK_OT_QuickEditorType.bl_idname,
        text="",
        icon=enums.EDITOR_TYPE_ICONS[ui_type],
    )
    operator.ui_type = ui_type
    # self.layout.separator()
    return None

class ARK_MT_PIE_SetEditorMode(bpy.types.Menu):
    bl_label = ""

    def draw(self, context):
        layout = self.layout.menu_pie()

        session = addon.session().interface
        pie_count = 0

        for ui_type, children in enums.EDITOR_MODE.items():
            pie_count += 1
            while pie_count in [3, 5, 6]:
                layout.separator()
                pie_count += 1

            operator = layout.operator(
                ARK_OT_SetEditorMode.bl_idname,
                icon = enums.EDITOR_TYPE_ICONS[ui_type]
            )
            operator.ui_type = ui_type
        return None
