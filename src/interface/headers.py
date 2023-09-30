# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import bl_ui

import utils
addon = utils.bpy.Addon()

from . import enums

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

def ARK_ASSETS_HT_draw(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.alert = True
    row.ui_units_x = 1.6
    bt = row.operator(
        f"{addon.name}.close_asset_browser",
        text = "X",
    )

    row = layout.row(align=True)
    ui_type = 'ASSETS'
    for ui_mode in enums.EDITOR_MODE[ui_type]:
        bt = row.operator(
            f"{addon.name}.set_editor_mode",
            text = "",
            icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
            depress = utils.bpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
        )
        bt.ui_type = ui_type
        bt.ui_mode = ui_mode

    row = layout.row(align=True)
    row.ui_units_x = 1
    row.prop(bpy.context.space_data.params, "asset_library_ref", text="")

    layout.separator()
    return None

def ARK_NODE_HT_draw(self, context):
    layout = self.layout

    box = layout.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['VIEW_3D'],
        emboss = False,
    )
    bt.ui_type = 'VIEW_3D'

    row = layout.row(align=True)
    ui_type = 'ShaderNodeTree'
    for ui_mode in enums.EDITOR_MODE[ui_type]:
        bt = row.operator(
            f"{addon.name}.set_editor_mode",
            text = "",
            icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
            depress = utils.bpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
        )
        bt.ui_type = ui_type
        bt.ui_mode = ui_mode

    row = self.layout.row(align=True)
    if not context.space_data.tree_type == "CompositorNodeTree":
        row.prop(context.space_data, "pin", text="", emboss=False)

    if context.space_data.id_from and context.active_object is not None and context.active_object.type != 'LIGHT':
        panel = row.template_ID(context.space_data.id_from, "active_material")

    layout.separator()
    return None

def ARK_OUTLINER_HT_draw(self, context):
    layout = self.layout

    box = layout.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['PROPERTIES'],
        emboss = False,
    )
    bt.ui_type = 'PROPERTIES'

    row = layout.row(align=True)
    ui_type = 'OUTLINER'
    orphan_loop = False
    for ui_mode in enums.EDITOR_MODE[ui_type]:
        if ui_mode.startswith("ORPHAN") and not orphan_loop:
            row = layout.row(align=True)
            row.alert = True
            orphan_loop = True
        bt = row.operator(
            f"{addon.name}.set_editor_mode",
            text = "",
            icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
            depress = utils.bpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
        )
        bt.ui_type = ui_type
        bt.ui_mode = ui_mode

    row = layout.row(align=True)
    row.alert = True
    bt = row.operator(
        "outliner.orphans_purge",
        text = "Purge",
    )
    bt.do_recursive = True

    layout.separator()
    return None

def ARK_PROPERTIES_HT_draw(self, context):
    layout = self.layout

    box = layout.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['OUTLINER'],
        emboss = False,
    )
    bt.ui_type = 'OUTLINER'

    layout.separator_spacer()

    layout.prop(context.space_data, "search_filter", icon='VIEWZOOM', text="")

    layout.separator_spacer()
    return None

def ARK_VIEW3D_HT_draw(self, context):
    layout = self.layout

    box = layout.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['ShaderNodeTree'],
        emboss = False,
    )
    bt.ui_type = 'ShaderNodeTree'

    row = layout.row(align=True)
    ui_type = 'VIEW_3D'
    for ui_mode in enums.EDITOR_MODE[ui_type]:
        bt = row.operator(
            f"{addon.name}.set_editor_mode",
            text = "",
            icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
            depress = utils.bpy.validate_props(enums.EDITOR_MODE[ui_type][ui_mode]),
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
            utils.bpy.ops.UTILS_OT_Placeholder.bl_idname,
            text = "",
            icon = 'CAMERA_STEREO',
        )
        sub.enabled = False

    row = layout.row(align=True)
    object_mode = 'OBJECT' if context.active_object is None else context.active_object.mode
    row.enabled = object_mode in {'OBJECT', 'EDIT'}
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

    layout.separator()
    return None

def enable():
    bpy.types.FILEBROWSER_HT_header.draw = ARK_ASSETS_HT_draw
    bpy.types.NODE_HT_header.draw = ARK_NODE_HT_draw
    bpy.types.OUTLINER_HT_header.draw = ARK_OUTLINER_HT_draw
    bpy.types.VIEW3D_HT_header.draw = ARK_VIEW3D_HT_draw
    bpy.types.PROPERTIES_HT_header.draw = ARK_PROPERTIES_HT_draw
    return None

def disable():
    import importlib
    importlib.reload(bl_ui.space_filebrowser)
    bpy.types.FILEBROWSER_HT_header.draw = bl_ui.space_filebrowser.FILEBROWSER_HT_header.draw
    importlib.reload(bl_ui.space_node)
    bpy.types.NODE_HT_header.draw = bl_ui.space_node.NODE_HT_header.draw
    importlib.reload(bl_ui.space_outliner)
    bpy.types.OUTLINER_HT_header.draw = bl_ui.space_outliner.OUTLINER_HT_header.draw
    importlib.reload(bl_ui.space_properties)
    bpy.types.PROPERTIES_HT_header.draw = bl_ui.space_properties.PROPERTIES_HT_header.draw
    importlib.reload(bl_ui.space_view3d)
    bpy.types.VIEW3D_HT_header.draw = bl_ui.space_view3d.VIEW3D_HT_header.draw
    return None

@addon.property
class WindowManager_Interface_Headers(bpy.types.PropertyGroup):
    def update_toggle(self, context):
        if self.toggle:
            enable()
        else:
            disable()
        return None

    toggle : bpy.props.BoolProperty(
        name = "Toogle",
        default = False,
        update = update_toggle,
    )

@addon.property
class Preferences_Interface_Headers(bpy.types.PropertyGroup):
    pass

CLASSES = [
    ARK_OT_VIEW3D_ZoomExtents,
    WindowManager_Interface_Headers,
    Preferences_Interface_Headers,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
