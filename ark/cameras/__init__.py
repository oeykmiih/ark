# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
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
        return ao is not None and ao.type == 'CAMERA' and ao.select_get() or context.scene.camera is not None

    def invoke(self, context, event):
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        preferences = addon.preferences
        ao = context.active_object

        if self.alt:
            for blcam in context.selected_objects:
                if blcam.type == 'CAMERA':
                    funops.duplicate_camera(blcam, preferences)
        elif ao is not None and ao.type == 'CAMERA':
            blcam = ao
            funops.duplicate_camera(blcam, preferences)
        elif context.scene.camera is not None:
            blcam = context.scene.camera
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
        return ao is not None and ao.type == 'CAMERA' and ao.select_get() or context.scene.camera is not None

    def invoke(self, context, event):
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        preferences = addon.preferences
        ao = context.active_object

        if self.alt:
            selected_cameras = [blob for blob in context.selected_objects if blob.type == 'CAMERA']
            if len(selected_cameras) > 0:
                funops.remove_cameras(
                    [blob for blob in context.selected_objects if blob.type == 'CAMERA'],
                    context,
                    preferences,
                )
                funops.set_next_camera_active(preferences)
            else:
                return {'CANCELLED'}
        elif ao is not None and ao.type == 'CAMERA':
            blcam = ao
            funops.remove_camera(blcam, context, preferences)
            funops.set_next_camera_active(preferences)
        elif context.scene.camera is not None:
            blcam = context.scene.camera
            funops.remove_camera(blcam, context, preferences)
            funops.set_next_camera_active(preferences)
        return {'FINISHED'}

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
        scene = context.scene
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
            funops.set_camera_list(session.cameras, blcol_cameras)
            blcam = scene.camera

            col = layout.column(align=True)
            header = col.box().row()
            col.template_list(
                    "ARK_UL_PROPERTIES_CameraList",
                    "Camera List",
                    session,
                    "cameras",
                    pr_scene,
                    "uilist_index",
                )

            info = header.row(align=True)
            buttons = header.row(align=True)

            buttons.alignment = 'RIGHT'
            buttons.operator(ARK_OT_AddCamera.bl_idname, text="", icon='ADD')
            buttons.operator(ARK_OT_RemoveCamera.bl_idname, text="", icon='REMOVE')
            buttons.operator(ARK_OT_DuplicateCamera.bl_idname, text="", icon='DUPLICATE')

            if len(session.cameras) == 0:
                utils.bpy.ui.alert(info, text=f"No camera in {blcol_cameras.name}.")
                # info.template_ID(scene, "camera", new=ARK_OT_AddCamera.bl_idname)
                return
            elif not blcam:
                utils.bpy.ui.label(info, text="No active camera.")
                return None
            else:
                if not view_combinations.collection_hierarchy.audit(blcam, preferences):
                    renamed = view_combinations.collection_hierarchy.audit_previous(blcam, preferences)
                    text = "%s" % "Camera was renamed, sync hierarchy?" if renamed else "Missing camera hierarchy, fix it?"
                    info.alert = True
                    info.operator(
                        ARK_OT_AddCameraHierarchy.bl_idname,
                        text = text,
                    ).renamed = renamed
                else:
                    info.label(text="")

                pr_cam = getattr(blcam.data, addon.name)

                box = layout.box()
                box.use_property_split = True
                box.use_property_decorate = False

                col = box.column(align=True)

                row = col.row(align=True)
                row.prop(pr_cam, "resolution_orientation", expand=True)

                row = utils.bpy.ui.split(col, text="Ratio")
                row.prop(pr_cam, "ratio_x", text="")
                row.prop(pr_cam, "ratio_y", text="")

                col.prop(pr_cam, "resolution_value")
                col.prop(
                    pr_cam,
                    "resolution_mode",
                    toggle = True,
                    text = "%s" % "Long Edge Resolution" if pr_cam.resolution_mode else "Short Edge Resolution",
                )

                row = utils.bpy.ui.split(col, text="Final Resolution", enabled=False)
                row.label(text=f"{scene.render.resolution_x}  x  {scene.render.resolution_y}")

                col = box.column(align=True)

                row = utils.bpy.ui.split(col, text="Clip")
                row.prop(blcam.data, "clip_start", text="")
                row.prop(blcam.data, "clip_end", text="")

                row = utils.bpy.ui.split(col, text="Shift")
                row.prop(blcam.data, "shift_x", text="", slider=True)
                row.prop(blcam.data, "shift_y", text="", slider=True)

                col = box.column(align=True)
                row = col.row(align=True)
                row.prop(pr_cam, "projection", expand=True)
                match pr_cam.projection:
                    case 'PERSP':
                        col.prop(blcam.data, "lens")
                    case 'ORTHO':
                        col.prop(blcam.data, "ortho_scale")
                    case _:
                        pass

                row = utils.bpy.ui.split(box, text="Perspective Correction")
                if funops.audit_camera_verticals(blcam):
                    utils.bpy.ui.label(row, text="Camera is vertical.")
                else:
                    row.alert = True
                    row.operator(
                        ARK_OT_ForceCameraVerticals.bl_idname,
                        text = "Camera is not vertical.",
                    )

                col = box.column(align=True)
                col.prop(pr_cam, "ev", slider=True)

                box = layout.box()
                box.use_property_split = True
                box.use_property_decorate = False

                col = box.column(align=False)

                row = utils.bpy.ui.split(col, text="Output")
                row.prop(scene.render, "filepath", text="")
                # TODO: improve handling of camera names and tokens
                ## hide it for now, default is '$camera'.
                # col.prop(pr_scene.render_queue, "fname", text="")

                col = box.column(align=True)
                col.row(align=True).prop(pr_scene.render_queue, "mode", expand=True)
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
        item = item.object
        pr_cam = getattr(item.data, addon.name)

        row = layout.row(align=True)
        row.prop(pr_cam, "render", text="")
        row.prop(bpy.data.objects[item.name], "name", text="")

        row = layout.row(align=True)
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

    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        helper_funcs = bpy.types.UI_UL_list

        filtered = []
        ordered = []
        items = [item.object for item in getattr(data, propname)]

        filtered = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "name", reverse=False)

        if self.use_filter_sort_alpha:
            ordered = helper_funcs.sort_items_by_name(items, 'name')
        return filtered, ordered

@addon.property
class Scene_Cameras(bpy.types.PropertyGroup):
    # NOTE: This patches uilist_index to never change, meaning it will
    ## never highlight a row, since we don't use the index in the first place.
    def set_uilist_index(self, value):
        self["uilist_index"] = -1
        return None

    def get_uilist_index(self):
        return self.get("uilist_index", -1)

    # NOTE: This index is just to fulfill call requirements,
    ## it's not used in the UIList to search for properties.
    uilist_index : bpy.props.IntProperty(
        name = "",
        default = -1,
        set = set_uilist_index,
        get = get_uilist_index,
    )

class WindowManager_Cameras_Cameras(bpy.types.PropertyGroup):
    object :  bpy.props.PointerProperty(type=bpy.types.Object)

@addon.property
class WindowManager_Cameras(bpy.types.PropertyGroup):
    cameras : bpy.props.CollectionProperty(type=WindowManager_Cameras_Cameras)
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

    for name in (name for name, module in MODULES.items() if hasattr(module, "UI")):
        module = MODULES[name]
        box = layout.box()
        box.label(text=name.replace("_", " ").title())
        properties = getattr(preferences, name)
        module.UI(properties, box)
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
    WindowManager_Cameras_Cameras,
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
