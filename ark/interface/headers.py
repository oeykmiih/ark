# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import bl_ui

from ark import utils
addon = utils.bpy.Addon()

from . import enums

class ARK_OT_VIEW3D_ZoomExtents(bpy.types.Operator):
    """Move view to scene extents."""
    bl_idname = f"{addon.name}.zoom_extents"
    bl_label = "Zoom Extents"
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
    if context.area.ui_type != 'ASSETS':
        return None

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
            depress = utils.bpy.validate_properties(enums.EDITOR_MODE[ui_type][ui_mode]),
        )
        bt.ui_type = ui_type
        bt.ui_mode = ui_mode

    row = layout.row(align=True)
    row.ui_units_x = 1
    row.prop(context.space_data.params, "asset_library_reference", text="")

    row = layout.row(align=True)
    row.prop(context.space_data.params, "filter_search", text="", icon='VIEWZOOM')

    layout.separator()
    return None

def ARK_NODE_HT_draw(self, context):
    layout = self.layout

    row = layout.row(align=True)
    box = row.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['VIEW_3D'],
        emboss = False,
    )
    bt.ui_type = 'VIEW_3D'

    sub = row.row(align=True)
    sub.ui_units_x = 1.0
    sub.prop(
        context.area,
        "ui_type",
        text = "",
        icon = 'DOWNARROW_HLT',
        icon_only = True,
    )

    row = layout.row(align=True)
    ui_type = 'ShaderNodeTree'
    for ui_mode in enums.EDITOR_MODE[ui_type]:
        bt = row.operator(
            f"{addon.name}.set_editor_mode",
            text = "",
            icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
            depress = context.space_data.shader_type == ui_mode,
        )
        bt.ui_type = ui_type
        bt.ui_mode = ui_mode

    row = self.layout.row(align=True)
    if not context.space_data.tree_type == "CompositorNodeTree":
        row.prop(context.space_data, "pin", text="", emboss=False)

    if context.space_data.id_from and context.active_object is not None and context.active_object.type != 'LIGHT':
        panel = row.template_ID(context.space_data.id_from, "active_material")

    layout.separator_spacer()

    row = layout.row(align=True)
    box = row.box()
    box.ui_units_x = 1.6
    box.prop(
        context.space_data,
        "show_region_ui",
        text = "",
        icon = 'RIGHTARROW',
        emboss = False,
    )
    return None

def ARK_OUTLINER_HT_draw(self, context):
    layout = self.layout

    row = layout.row(align=True)
    box = row.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['PROPERTIES'],
        emboss = False,
    )
    bt.ui_type = 'PROPERTIES'

    sub = row.row(align=True)
    sub.ui_units_x = 1.0
    sub.prop(
        context.area,
        "ui_type",
        text = "",
        icon = 'DOWNARROW_HLT',
        icon_only = True,
    )

    row = layout.row(align=True)
    ui_type = 'OUTLINER'
    orphan_loop = False
    for ui_mode in enums.EDITOR_MODE[ui_type]:
        if not orphan_loop and ui_mode.startswith("ORPHAN"):

            layout.prop(context.space_data, "filter_text", icon='VIEWZOOM', text="")

            row = layout.row(align=True)
            row.alert = True
            orphan_loop = True
        bt = row.operator(
            f"{addon.name}.set_editor_mode",
            text = "",
            icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
            depress = utils.bpy.validate_properties(enums.EDITOR_MODE[ui_type][ui_mode]),
        )
        bt.ui_type = ui_type
        bt.ui_mode = ui_mode

    row = layout.row(align=True)
    row.alert = True
    bt = row.operator("outliner.orphans_purge", icon='TRASH', text="")
    bt.do_recursive = True

    layout.separator()
    return None

def ARK_PROPERTIES_HT_draw(self, context):
    layout = self.layout

    row = layout.row(align=True)
    box = row.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['OUTLINER'],
        emboss = False,
    )
    bt.ui_type = 'OUTLINER'

    sub = row.row(align=True)
    sub.ui_units_x = 1.0
    sub.prop(
        context.area,
        "ui_type",
        text = "",
        icon = 'DOWNARROW_HLT',
        icon_only = True,
    )

    layout.separator_spacer()

    layout.prop(context.space_data, "search_filter", icon='VIEWZOOM', text="")

    layout.separator_spacer()
    return None

def ARK_VIEW3D_HT_draw(self, context):
    layout = self.layout

    row = layout.row(align=True)
    box = row.box()
    box.ui_units_x = 1.6
    bt = box.operator(
        f"{addon.name}.quick_editor_type",
        text = "",
        icon = enums.EDITOR_TYPE_ICONS['ShaderNodeTree'],
        emboss = False,
    )
    bt.ui_type = 'ShaderNodeTree'

    sub = row.row(align=True)
    sub.ui_units_x = 1.0
    sub.prop(
        context.area,
        "ui_type",
        text = "",
        icon = 'DOWNARROW_HLT',
        icon_only = True,
    )

    row = layout.row(align=True)
    ui_type = 'VIEW_3D'
    for ui_mode in enums.EDITOR_MODE[ui_type]:
        bt = row.operator(
            f"{addon.name}.set_editor_mode",
            text = "",
            icon = enums.EDITOR_MODE_ICONS[ui_type][ui_mode],
            depress = utils.bpy.validate_properties(enums.EDITOR_MODE[ui_type][ui_mode]),
        )
        bt.ui_type = ui_type
        bt.ui_mode = ui_mode
    row.popover(panel="VIEW3D_PT_shading", text="")

    row = layout.row(align=True)

    sub = row.row(align=True)
    bt = sub.operator(
        "view3d.view_camera",
        text = "",
        icon = 'CAMERA_DATA',
        depress = (context.area.spaces.active.region_3d.view_perspective == 'CAMERA'),
        )
    sub.enabled = context.scene.camera is not None

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
    bt = row.prop(
        context.space_data.overlay,
        "show_outline_selected",
        text = "",
        icon = 'MESH_CUBE',
    )
    row.popover(panel="VIEW3D_PT_overlay", text="")

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


    snap_items = bpy.types.ToolSettings.bl_rna.properties["snap_elements"].enum_items
    snap_elements = context.tool_settings.snap_elements
    if len(snap_elements) == 1:
        text = ""
        for elem in snap_elements:
            icon = snap_items[elem].icon
            break
    else:
        text = "Mix"
        icon = 'NONE'
    del snap_items, snap_elements

    row.prop(context.tool_settings, "use_snap", text="")
    sub = row.row(align=True)
    sub.popover(
        panel="VIEW3D_PT_snapping",
        icon=icon,
        text=text,
    )

    layout.separator_spacer()

    row = layout.row(align=True)
    box = row.box()
    box.ui_units_x = 1.6
    box.prop(
        context.space_data,
        "show_region_ui",
        text = "",
        icon = 'RIGHTARROW',
        emboss = False,
    )
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
