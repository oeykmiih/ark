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

class ARK_OT_VIEW3D_ZoomExtents(bpy.types.Operator):
    bl_idname = f"{addon.name}.zoom_extents"
    bl_label = ""
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'VIEW_3D'

    def execute(self, context):
        if context.area.spaces.active.region_3d.view_perspective != 'CAMERA':
            bpy.ops.view3d.view_all()
            pass
        else:
            bpy.ops.view3d.view_center_camera()
        return {"INTERFACE"}

def ARK_OUTLINER_HT_draw(self, context):
    layout = self.layout

    bt = layout.operator(
        ARK_OT_QuickEditorType.bl_idname,
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['PROPERTIES'],
    )
    bt.ui_type = 'PROPERTIES'

    row = layout.row(align=True)
    ui_type = 'OUTLINER'
    ui_mode = 'VIEW_LAYER'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    ui_mode = 'FILE'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    ui_mode = 'FILE_MATERIAL'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    ui_mode = 'FILE_NODETREE'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    layout.separator()

    row = layout.row(align=True)
    bt = row.operator(
        "outliner.orphans_purge",
        text = "Purge",
    )
    bt.do_recursive = True

    layout.separator()

    row = layout.row(align=True)
    ui_mode = 'ORPHAN'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    ui_mode = 'ORPHAN_MATERIAL'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    ui_mode = 'ORPHAN_NODETREE'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    layout.separator_spacer()
    return None

def ARK_VIEW3D_HT_draw(self, context):
    layout = self.layout

    bt = layout.operator(
        ARK_OT_QuickEditorType.bl_idname,
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['ShaderNodeTree'],
    )
    bt.ui_type = 'ShaderNodeTree'

    row = layout.row(align=True)
    ui_type = 'VIEW_3D'
    ui_mode = 'WIREFRAME'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode])
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    ui_mode = 'SOLID'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode])
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    ui_mode = 'RENDERED'
    bt = row.operator(
        ARK_OT_SetEditorMode.bl_idname,
        text = "",
        icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
        depress = utils.blpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode])
    )
    bt.ui_type = ui_type
    bt.ui_mode = ui_mode

    row = layout.row(align=True)
    bt = row.operator(
        "view3d.view_selected",
        text = "",
        icon = 'ZOOM_IN',
    )

    bt = row.operator(
        ARK_OT_VIEW3D_ZoomExtents.bl_idname,
        text = "",
        icon = 'VIEW_ZOOM',
    )

    bt = row.operator(
        "view3d.view_camera",
        text = "",
        icon = 'CAMERA_DATA',
        depress = (context.area.spaces.active.region_3d.view_perspective == 'CAMERA'),
        )

    row = layout.row(align=True)
    bt = row.prop(
        context.space_data.overlay,
        "show_outline_selected",
        text = "",
        icon = 'MESH_CUBE',
    )

    row = layout.row(align=True)
    row.prop(context.scene.render,
        "film_transparent",
        text = "",
        icon = 'WORLD',
    )

    sub = row.row(align=True)
    sub.prop(context.scene.render,
        "use_border",
        text = "",
        icon = 'SHADING_BBOX',
    )

    if context.scene.camera:
        sub.prop(
            context.scene.camera.data,
            "show_passepartout",
            text = "",
            icon = 'CAMERA_STEREO',
        )
    else:
        sub.operator(
            utils.UTILS_OT_Placeholder.bl_idname,
            text = "",
            icon = 'CAMERA_STEREO',
        )
        sub.enabled = False

    row = layout.row(align=True)
    object_mode = 'OBJECT' if context.active_object is None else context.active_object.mode
    if object_mode not in {'OBJECT', 'EDIT'}:
        row.enabled = False
    row.prop(
        context.tool_settings,
        "transform_pivot_point",
        text = "",
        icon_only = True,
    )

    row.prop_with_popover(
        context.scene.transform_orientation_slots[0],
        "type",
        text = "",
        panel = "VIEW3D_PT_transform_orientations",
        icon_only = True,
    )

    layout.separator_spacer()
    return None
