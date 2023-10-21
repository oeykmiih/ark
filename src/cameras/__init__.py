# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import utils
addon = utils.bpy.Addon()

from . import funops

MODULES = {
    "properties" : None,
    "render_queue" : None,
    "view_combinations" : None,
}
MODULES = utils.import_modules(MODULES)

class ark_hierarchy():
    @staticmethod
    def create(preferences, context):
        blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, force=True, parent=context.scene.collection)
        blcol_blockouts = utils.bpy.col.obt(preferences.container_blockouts, force=True, parent=blcol_cameras)
        blcol_props = utils.bpy.col.obt(preferences.container_props, force=True, parent=context.scene.collection)
        return None

    @staticmethod
    def audit(preferences):
        conditions = [
            utils.bpy.col.obt(preferences.container_cameras, local=True),
            utils.bpy.col.obt(preferences.container_blockouts, local=True),
            utils.bpy.col.obt(preferences.container_props, local=True),
        ]
        return all(conditions)

class ARK_OT_CreateArkHierarchy(bpy.types.Operator):
    bl_idname = f"{addon.name}.create_ark_hierarchy"
    bl_label = ""
    bl_options = {'UNDO' , 'INTERNAL'}

    def execute(self, context):
        preferences = addon.preferences
        ark_hierarchy.create(preferences, context)
        return {'FINISHED'}

class ARK_OT_AddCameraHierarchy(bpy.types.Operator):
    bl_idname = f"{addon.name}.add_camera_hierarchy"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    renamed : bpy.props.BoolProperty(default = False)

    def execute(self, context):
        preferences = addon.preferences
        blcam = context.scene.camera

        funops.add_camera_hierarchy(blcam, preferences, renamed=self.renamed)
        return {'FINISHED'}

class ARK_OT_SetCameraActive(bpy.types.Operator):
    bl_idname = f"{addon.name}.set_camera_active"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    name: bpy.props.StringProperty()

    def execute(self, context):
        preferences = addon.preferences
        blcam = context.scene.camera = bpy.data.objects.get(self.name)

        funops.set_camera_active(blcam, preferences)
        return {'FINISHED'}

class ARK_OT_AddCamera(bpy.types.Operator):
    bl_idname = f"{addon.name}.add_camera"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        preferences = addon.preferences

        funops.add_camera(preferences)
        return {'FINISHED'}

class ARK_OT_DuplicateCamera(bpy.types.Operator):
    bl_idname = f"{addon.name}.duplicate_camera"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    alt : bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        ao = context.active_object
        return ao is not None and ao.type == 'CAMERA' and ao.select_get()

    def invoke(self, context, event):
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        preferences = addon.preferences

        if self.alt:
            for blcam in context.selected_objects:
                if blcam.type == 'CAMERA':
                    funops.duplicate_camera(blcam, preferences)
        else:
            blcam = context.active_object
            funops.duplicate_camera(blcam, preferences)
        return {'FINISHED'}

class ARK_OT_RemoveCamera(bpy.types.Operator):
    bl_idname = f"{addon.name}.remove_camera"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    alt : bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        ao = context.active_object
        return ao is not None and ao.type == 'CAMERA' and ao.select_get()

    def invoke(self, context, event):
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        preferences = addon.preferences

        if self.alt:
            for blcam in context.selected_objects:
                if blcam.type == 'CAMERA':
                    funops.remove_camera(blcam, preferences)
        else:
            blcam = context.active_object
            funops.remove_camera(blcam, preferences)
        return {'FINISHED'}

class ARK_OT_ForceCameraVerticals(bpy.types.Operator):
    bl_idname = f"{addon.name}.force_camera_verticals"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    alt : bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.scene.camera

    def invoke(self, context, event):
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        if self.alt:
            for blcam in context.selected_objects:
                if blcam.type == 'CAMERA':
                    funops.force_camera_verticals(blcam)
            if context.scene.camera not in context.selected_objects:
                funops.force_camera_verticals(context.scene.camera)
        else:
            blcam = context.scene.camera
            funops.force_camera_verticals(blcam)
        return {'FINISHED'}

class ARK_PT_PROPERTIES_Scene(bpy.types.Panel):
    bl_label = "Cameras"
    bl_idname = "ARK_PT_PROPERTIES_Scene"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        preferences = addon.preferences
        session = addon.session
        pr_scene = addon.get_property("scene")
        blcol_cameras = None
        cam_list = None
        pr_cam = None

        if not ark_hierarchy.audit(preferences):
            box = layout.box()
            row = box.row()
            row.alert = True
            row.operator(
                ARK_OT_CreateArkHierarchy.bl_idname,
                text = "Missing structure for cameras, fix it?",
            )
            return None
        else:
            blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, local=True)
            cam_list = funops.get_camera_list(blcol_cameras)
            blcam = context.scene.camera

            box = layout.box()
            row = box.row()
            row.template_list(
                    "ARK_UL_PROPERTIES_CameraList",
                    "Camera List",
                    blcol_cameras,
                    "all_objects",
                    pr_scene,
                    "uilist_index",
                )
            col = row.column(align=True)
            col.operator(ARK_OT_AddCamera.bl_idname, text="", icon='ADD')
            col.operator(ARK_OT_RemoveCamera.bl_idname, text="", icon='REMOVE')
            col.operator(ARK_OT_DuplicateCamera.bl_idname, text="", icon='DUPLICATE')

        if not cam_list:
            row = box.row()
            utils.bpy.ui.alert(row, text=f"No camera in {blcol_cameras.name}.")
            return None
        elif not blcam:
            row = box.row(align=True)
            utils.bpy.ui.label(row, text="No active camera.")
            return None
        elif not view_combinations.collection_hierarchy.audit(blcam, preferences):
            renamed = view_combinations.collection_hierarchy.audit_previous(blcam, preferences)
            text = "%s" % "Camera was renamed, sync hierarchy?" if renamed else "Missing camera hierarchy, fix it?"
            row = box.row()
            row.alert = True
            row.operator(
                ARK_OT_AddCameraHierarchy.bl_idname,
                text = text,
            ).renamed = renamed
        else:
            box.row().label(text="")

        pr_cam = getattr(blcam.data, addon.name)
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(pr_cam, "resolution_orientation", expand=True)
        row = col.row(align=True)
        row.prop(pr_cam, "ratio_x")
        row.prop(pr_cam, "ratio_y")
        col.prop(pr_cam, "resolution_value")
        col.prop(
            pr_cam,
            "resolution_mode",
            toggle = True,
            text = "%s" % "Long Edge Resolution" if pr_cam.resolution_mode else "Short Edge Resolution",
        )
        row = col.row()
        row.enabled = False
        row.label(text=f"Final Resolution: {context.scene.render.resolution_x}x{context.scene.render.resolution_y}")

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(blcam.data, "clip_start")
        row.prop(blcam.data, "clip_end")
        row = col.row(align=True)
        row.prop(blcam.data, "shift_x", slider=True)
        row.prop(blcam.data, "shift_y", slider=True)

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(pr_cam, "projection", expand=True)
        row = col.row(align=True)
        match pr_cam.projection:
            case 'PERSP':
                col.prop(blcam.data, "lens")
            case 'ORTHO':
                col.prop(blcam.data, "ortho_scale")
            case _:
                pass

        row = box.row()
        if funops.audit_camera_verticals(blcam):
            utils.bpy.ui.label(row, text="Camera is vertical.", depress=True)
        else:
            row.alert = True
            row.operator(
                ARK_OT_ForceCameraVerticals.bl_idname,
                text = "Camera is not vertical.",
            )

        col = box.column(align=True)
        row = col.row()
        row.prop(pr_cam, "exposure_mode", expand=True)
        match pr_cam.exposure_mode:
            case 'EV':
                col.prop(pr_cam, "ev", slider=True)
            case 'MANUAL':
                col.prop(pr_cam, "aperture")
                col.prop(pr_cam, "shutter_speed")
                col.prop(pr_cam, "iso")

        box = layout.box()
        col = box.column(align=False)
        col.prop(context.scene.render, "filepath", text="")
        # TODO: improve handling of camera names and tokens
        ## hide it for now, default is '$camera'.
        # col.prop(pr_scene.render_queue, "fname", text="")

        col = box.column(align=True)
        sub = col.row()
        sub.prop(pr_scene.render_queue, "mode", expand=True)
        col.prop(pr_scene.render_queue, "slots", toggle=True)
        col.prop(pr_scene.render_queue, "export", toggle=True)

        col = box.column(align=True)
        op = col.operator(
            render_queue.ARK_OT_RenderQueue.bl_idname,
            text="Render!",
        )
        op.mode = pr_scene.render_queue.mode
        op.slots = pr_scene.render_queue.slots
        op.export = pr_scene.render_queue.export
        op.fname = pr_scene.render_queue.fname
        return None

class ARK_UL_PROPERTIES_CameraList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        pr_cam = getattr(item.data, addon.name)

        row.prop(pr_cam, "render", text="")

        row.prop(bpy.data.objects[item.name], "name", text="")

        op = row.operator(
            utils.bpy.ops.UTILS_OT_Select.bl_idname,
            text = "",
            icon = '%s' % 'RESTRICT_SELECT_OFF' if item.select_get() or item.parent is not None and item.parent.select_get() else 'RESTRICT_SELECT_ON',
            emboss= context.active_object == item and item.select_get(),
        )
        op.obj_name = item.name
        op.parent_instead = True

        op = row.operator(
            ARK_OT_SetCameraActive.bl_idname,
            text = "",
            icon = '%s' % 'RESTRICT_RENDER_OFF' if context.scene.camera == item else 'RESTRICT_RENDER_ON',
            emboss = context.scene.camera == item,
        )
        op.name=item.name
        return None

    def draw_filter(self, context, layout):
        return None

    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        helper_funcs = bpy.types.UI_UL_list

        filtered = []
        ordered = []
        items = getattr(data, propname)

        ordered = helper_funcs.sort_items_by_name(items, 'name')

        # Initialize with all items visible
        filtered = [self.bitflag_filter_item] * len(items)
        # Filtering out the first item
        for i, item in enumerate(items):
            if item.type != 'CAMERA':
                filtered[i] &= ~self.bitflag_filter_item

        return filtered, ordered

@addon.property
class Scene_Cameras(bpy.types.PropertyGroup):
    # NOTE: This patches uilist_index to never be changed, meaning it will
    ## never highlight a row, since we don't use the index in the first place.
    def update_uilist_index(self, context):
        self.uilist_index = 9999
        return None

    # NOTE: This index is just to fulfill call requirements,
    ## it's not used in the UIList to search for properties.
    uilist_index : bpy.props.IntProperty(
        name = "",
        default = 9999,
        update = update_uilist_index,
    )

@addon.property
class WindowManager_Cameras(bpy.types.PropertyGroup):
    pass

@addon.property
class Preferences_Cameras(bpy.types.PropertyGroup):
    default_name : bpy.props.StringProperty(
        name="Camera Name",
        default="Cam",
    )

    container_blockouts : bpy.props.StringProperty(
        name="Blockouts",
        default="#Blockouts",
    )

    container_cameras : bpy.props.StringProperty(
        name="Cameras",
        default="#Cameras",
    )

    container_props : bpy.props.StringProperty(
        name="Props",
        default="#Props",
    )

    trackers_camera : bpy.props.StringProperty(
        name="Camera Tracker",
        default="#CameraTracker",
    )

def UI(preferences, layout):
    box = layout.box()
    box.prop(preferences, "container_cameras")
    box.prop(preferences, "container_props")
    box.prop(preferences, "container_blockouts")
    box.prop(preferences, "trackers_camera")

    items = (name for name, module in MODULES.items() if hasattr(module, "UI"))
    for name in items:
        module = MODULES[name]
        properties = getattr(preferences, name)
        layout = layout.box()
        module.UI(properties, layout)
    return None

CLASSES = [
    ARK_OT_CreateArkHierarchy,
    ARK_OT_AddCameraHierarchy,
    ARK_OT_SetCameraActive,
    ARK_OT_AddCamera,
    ARK_OT_DuplicateCamera,
    ARK_OT_RemoveCamera,
    ARK_OT_ForceCameraVerticals,
    ARK_UL_PROPERTIES_CameraList,
    ARK_PT_PROPERTIES_Scene,
    WindowManager_Cameras,
    Preferences_Cameras,
    Scene_Cameras,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    utils.bpy.unregister_modules(MODULES)
    return None
