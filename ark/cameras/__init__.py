# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
addon = utils.bpy.Addon()

MODULES = {
    "common" : None,
    "render_queue" : None,
    "view_combinations" : None,
    "properties" : None, #NOTE: Should be last to register.
}
MODULES = utils.import_modules(MODULES)

class ark_hierarchy():
    @staticmethod
    def create(preferences, context):
        blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, force=True, parent=context.scene.collection)
        blcol_viewcombinations = utils.bpy.col.obt(preferences.container_viewcombinations, force=True, parent=context.scene.collection)
        return None

    @staticmethod
    def audit(preferences):
        conditions = [
            utils.bpy.col.obt(preferences.container_cameras, local=True),
            utils.bpy.col.obt(preferences.container_viewcombinations, local=True),
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
        bl_cam = context.scene.camera

        common.add_camera_hierarchy(bl_cam, preferences, renamed=self.renamed)
        return {'FINISHED'}

class ARK_OT_SetCameraActive(bpy.types.Operator):
    bl_idname = f"{addon.name}.set_camera_active"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    name: bpy.props.StringProperty()

    def execute(self, context):
        preferences = addon.preferences
        bl_cam = context.scene.camera = bpy.data.objects.get(self.name)

        common.set_camera_active(bl_cam, preferences)
        return {'FINISHED'}

class ARK_OT_AddCamera(bpy.types.Operator):
    bl_idname = f"{addon.name}.add_camera"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        preferences = addon.preferences

        common.add_camera(preferences)
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
            for bl_cam in context.selected_objects:
                if bl_cam.type == 'CAMERA':
                    common.duplicate_camera(bl_cam, preferences)
        elif ao is not None and ao.type == 'CAMERA':
            bl_cam = ao
            common.duplicate_camera(bl_cam, preferences)
        elif context.scene.camera is not None:
            bl_cam = context.scene.camera
            common.duplicate_camera(bl_cam, preferences)
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
                common.remove_cameras(
                    [blob for blob in context.selected_objects if blob.type == 'CAMERA'],
                    context,
                    preferences,
                )
                common.set_next_camera_active(preferences)
            else:
                return {'CANCELLED'}
        elif ao is not None and ao.type == 'CAMERA':
            bl_cam = ao
            common.remove_camera(bl_cam, context, preferences)
            common.set_next_camera_active(preferences)
        elif context.scene.camera is not None:
            bl_cam = context.scene.camera
            common.remove_camera(bl_cam, context, preferences)
            common.set_next_camera_active(preferences)
        return {'FINISHED'}

class ARK_OT_AddActiveToViewCombination(bpy.types.Operator):
    bl_idname = f"{addon.name}.add_active_to_view_combination"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    name : bpy.props.StringProperty()

    def execute(self, context):
        bl_cam = bpy.data.objects[self.name]
        ao = context.active_object

        view_combinations.collection_hierarchy.get_viewcombination(bl_cam).objects.link(ao)
        return {'FINISHED'}

class ARK_OT_RemoveActiveFromViewCombination(bpy.types.Operator):
    bl_idname = f"{addon.name}.remove_active_from_view_combination"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    name : bpy.props.StringProperty()

    def execute(self, context):
        bl_cam = bpy.data.objects[self.name]
        ao = context.active_object

        view_combinations.collection_hierarchy.get_viewcombination(bl_cam).objects.unlink(ao)
        return {'FINISHED'}

class ARK_OT_SetActiveAsBlockout(bpy.types.Operator):
    bl_idname = f"{addon.name}.set_active_as_blockout"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    @staticmethod
    def conditions(context):
        ao = context.active_object
        conditions = [
            ao.visible_camera == True,
            ao.visible_diffuse == True,
            ao.visible_glossy == True,
            ao.visible_transmission == True,
            ao.visible_volume_scatter == True,
        ]
        return all(conditions)

    def execute(self, context):
        ao = context.active_object
        ao.visible_camera = False
        ao.visible_diffuse = False
        ao.visible_glossy = False
        ao.visible_transmission = False
        ao.visible_volume_scatter = False
        return {'FINISHED'}

class ARK_OT_UnsetActiveAsBlockout(bpy.types.Operator):
    bl_idname = f"{addon.name}.unset_active_as_blockout"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    @staticmethod
    def conditions(context):
        ao = context.active_object
        conditions = [
            ao.visible_camera == False,
            ao.visible_diffuse == False,
            ao.visible_glossy == False,
            ao.visible_transmission == False,
            ao.visible_volume_scatter == False,
        ]
        return all(conditions)

    def execute(self, context):
        ao = context.active_object
        ao.visible_camera = True
        ao.visible_diffuse = True
        ao.visible_glossy = True
        ao.visible_transmission = True
        ao.visible_volume_scatter = True
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
            for bl_cam in context.selected_objects:
                if bl_cam.type == 'CAMERA':
                    common.force_camera_verticals(bl_cam)
            if context.scene.camera not in context.selected_objects:
                common.force_camera_verticals(context.scene.camera)
        else:
            bl_cam = context.scene.camera
            common.force_camera_verticals(bl_cam)
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

        col = layout.column(align=True)
        header = col.box().row()
        info = header.row(align=True)
        buttons = header.row(align=True)
        buttons.alignment = 'RIGHT'

        if not ark_hierarchy.audit(preferences):
            info.alert = True
            info.operator(ARK_OT_CreateArkHierarchy.bl_idname, text="Missing collections, fix it?")
            utils.bpy.ui.empty(buttons, emboss=False)
            buttons.scale_x = 3.0
        else:
            body = col.box()

            blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, local=True)
            common.set_camera_list(session.cameras, blcol_cameras)
            bl_cam = scene.camera

            body.template_list(
                    "ARK_UL_PROPERTIES_CameraList",
                    "Camera List",
                    session,
                    "cameras",
                    pr_scene,
                    "uilist_index",
                )

            buttons.operator(ARK_OT_AddCamera.bl_idname, text="", icon='ADD')
            buttons.operator(ARK_OT_RemoveCamera.bl_idname, text="", icon='REMOVE')
            buttons.operator(ARK_OT_DuplicateCamera.bl_idname, text="", icon='DUPLICATE')

            if len(session.cameras) == 0:
                utils.bpy.ui.label(info, text=f"No camera in {blcol_cameras.name}.")
            elif not bl_cam:
                utils.bpy.ui.label(info, text="No active camera.")
            else:
                if not view_combinations.collection_hierarchy.audit(bl_cam, preferences):
                    renamed = view_combinations.collection_hierarchy.audit_previous(bl_cam, preferences)
                    text = "%s" % "Camera was renamed, sync hierarchy?" if renamed else "Missing camera hierarchy, fix it?"
                    info.alert = True
                    info.operator(
                        ARK_OT_AddCameraHierarchy.bl_idname,
                        text = text,
                    ).renamed = renamed
                else:
                    info.label(text="")

                pr_cam = getattr(bl_cam.data, addon.name)

                section = layout.box()
                section.use_property_split = True
                section.use_property_decorate = False

                col = section.column(align=True)

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
                utils.bpy.ui.label(row, text=f"{scene.render.resolution_x}  x  {scene.render.resolution_y}")

                col = section.column(align=True)

                row = utils.bpy.ui.split(col, text="Clip")
                row.prop(bl_cam.data, "clip_start", text="")
                row.prop(bl_cam.data, "clip_end", text="")

                row = utils.bpy.ui.split(col, text="Shift")
                row.prop(bl_cam.data, "shift_x", text="", slider=True)
                row.prop(bl_cam.data, "shift_y", text="", slider=True)

                col = section.column(align=True)
                row = col.row(align=True)
                row.prop(pr_cam, "projection", expand=True)
                match pr_cam.projection:
                    case 'PERSP':
                        col.prop(bl_cam.data, "lens")
                    case 'ORTHO':
                        col.prop(bl_cam.data, "ortho_scale")
                    case _:
                        pass

                row = utils.bpy.ui.split(section, text="Perspective Correction")
                if common.audit_camera_verticals(bl_cam):
                    utils.bpy.ui.label(row, text="Camera is vertical.")
                else:
                    row.alert = True
                    row.operator(
                        ARK_OT_ForceCameraVerticals.bl_idname,
                        text = "Camera is not vertical.",
                    )

                col = section.column(align=True)
                col.prop(pr_cam, "ev", slider=True)

                section = layout.box()
                section.use_property_split = True
                section.use_property_decorate = False

                col = section.column(align=False)

                row = utils.bpy.ui.split(col, text="Output Path")
                row.prop(scene.render, "filepath", text="")
                row = utils.bpy.ui.split(col, text="Final Path", enabled=False)
                sub = row.box()
                sub.ui_units_y = 1.0
                sub.scale_y = 1 / 2.0
                sub.label(text=render_queue.preview_path(context))
                # TODO: improve handling of camera names and tokens

                col = section.column(align=True)
                col.row(align=True).prop(pr_scene.render_queue, "mode", expand=True)
                col.prop(pr_scene.render_queue, "slots", toggle=True)
                col.prop(pr_scene.render_queue, "export", toggle=True)

                col = section.column(align=True)
                op = col.operator(
                    render_queue.ARK_OT_RenderQueue.bl_idname,
                    text="Render!",
                )
                op.mode = pr_scene.render_queue.mode
                op.slots = pr_scene.render_queue.slots
                op.export = pr_scene.render_queue.export
        return None

class ARK_UL_PROPERTIES_CameraList(bpy.types.UIList):
    def _viewcombinations(self, context, layout, item):
        ao = context.active_object
        blcol_cam_viewcombination = view_combinations.collection_hierarchy.get_viewcombination(item)

        layout = layout.row(align=True)
        if ao is None or not ao.select_get() or blcol_cam_viewcombination is None:
            layout.enabled = False
            layout.operator(utils.bpy.ops.UTILS_OT_Placeholder.bl_idname, icon='BLANK1', emboss=False)
            layout.operator(utils.bpy.ops.UTILS_OT_Placeholder.bl_idname, icon='BLANK1', emboss=False)
        else:
            _ = True
            if ao.name not in blcol_cam_viewcombination.objects:
                layout.operator(ARK_OT_AddActiveToViewCombination.bl_idname, icon='HIDE_ON', emboss=False).name = item.name
                _ = False
            else:
                layout.operator(ARK_OT_RemoveActiveFromViewCombination.bl_idname, icon='HIDE_OFF', depress=True).name = item.name

            sub = layout.row()
            sub.enabled = _
            if ARK_OT_SetActiveAsBlockout.conditions(context):
                sub.operator(ARK_OT_SetActiveAsBlockout.bl_idname, icon='SNAP_VOLUME', emboss=False)
            else:
                sub.operator(ARK_OT_UnsetActiveAsBlockout.bl_idname, icon='META_CUBE', emboss=False)
        return None

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        item = item.object
        pr_cam = getattr(item.data, addon.name)

        row = layout.row(align=True)
        row.prop(pr_cam, "render", text="")
        row.prop(item, "name", text="")

        row = layout.row()
        row.alignment = 'RIGHT'

        self._viewcombinations(context, row, item)

        sub = row.row(align=True)
        op = sub.operator(
            utils.bpy.ops.UTILS_OT_Select.bl_idname,
            text = "",
            icon = '%s' % 'RESTRICT_SELECT_OFF' if item.select_get() or item.parent is not None and item.parent.select_get() else 'RESTRICT_SELECT_ON',
            emboss= context.active_object == item and item.select_get(),
        )
        op.obj_name = item.name
        op.parent_instead = True

        op = sub.operator(
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
    object : bpy.props.PointerProperty(type=bpy.types.Object)

@addon.property
class WindowManager_Cameras(bpy.types.PropertyGroup):
    cameras : bpy.props.CollectionProperty(type=WindowManager_Cameras_Cameras)

@addon.property
class Preferences_Cameras(bpy.types.PropertyGroup):
    default_name : bpy.props.StringProperty(
        name = "Default Camera Name",
        default = "Cam",
    )

    container_cameras : bpy.props.StringProperty(
        name = "Cameras",
        default = "#Cameras",
    )

    container_props : bpy.props.StringProperty(
        name = "Collection Props",
        description = "Collection name where to store all Props",
        default = "#Props",
    )

    container_viewcombinations : bpy.props.StringProperty(
        name = "View Combinations",
        description = "Collection name where to store all View Combinations",
        default = "#ViewCombinations",
    )

    trackers_camera : bpy.props.StringProperty(
        name="Camera Tracker",
        default="#CameraTracker",
    )

def UI(preferences, layout):
    box = layout.box()
    box.prop(preferences, "container_cameras")
    box.prop(preferences, "container_props")
    box.prop(preferences, "container_viewcombinations")
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
    ARK_OT_AddActiveToViewCombination,
    ARK_OT_RemoveActiveFromViewCombination,
    ARK_OT_SetActiveAsBlockout,
    ARK_OT_UnsetActiveAsBlockout,
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
