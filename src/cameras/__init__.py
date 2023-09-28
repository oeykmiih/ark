# SPDX-License-Identifier: GPL-2.0-or-later
import importlib
import math
import enum

import bpy
import utils
addon = utils.bpy.Addon()

MODULES = {
    "properties" : None,
    "view_combinations" : None,
}
MODULES = utils.import_modules(MODULES)

class ArkHierarchy():
    @staticmethod
    def create(context):
        preferences = addon.preferences
        blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, force=True, parent=context.scene.collection)
        blcol_blockouts = utils.bpy.col.obt(preferences.container_blockouts, force=True, parent=context.scene.collection)
        blcol_props = utils.bpy.col.obt(preferences.container_props, force=True, parent=context.scene.collection)
        return None

    @staticmethod
    def audit(context):
        preferences = addon.preferences
        conditions = [
            utils.bpy.col.obt(preferences.container_blockouts, local=True),
            utils.bpy.col.obt(preferences.container_props, local=True),
        ]
        return all(conditions)

class ARK_OT_CreateArkHierarchy(bpy.types.Operator, ArkHierarchy):
    bl_idname = f"{addon.name}.create_ark_hierarchy"
    bl_label = ""
    bl_options = {'UNDO' , 'INTERNAL'}

    def execute(self, context):
        self.create(context)
        return {'FINISHED'}

class ARK_OT_AddCameraHierarchy(bpy.types.Operator, view_combinations.CollectionHierarchy):
    bl_idname = f"{addon.name}.add_camera_hierarchy"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    renamed : bpy.props.BoolProperty(default = False)

    def execute(self, context):
        blcam = context.scene.camera
        if self.renamed:
            self.update(context, blcam)
        else:
            self.create(context, blcam)
        self.save_refs(context, blcam)
        return {'FINISHED'}

class ARK_OT_SetCameraActive(bpy.types.Operator):
    bl_idname = f"{addon.name}.set_camera_active"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    name: bpy.props.StringProperty()

    def execute(self, context):
        preferences = addon.preferences
        cam = context.scene.camera = bpy.data.objects.get(self.name)
        props_cam = getattr(cam.data, addon.name)
        blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, local=True)

        tracker = utils.bpy.obj.obt(preferences.trackers_camera, parent=blcol_cameras, force=True, local=True)
        tracker.matrix_world = cam.matrix_world
        tracker.use_fake_user = True
        tracker.hide_select = True
        tracker.hide_viewport = True

        self.update_cam_properties(context, props_cam)
        return {'FINISHED'}

    def update_cam_properties(self, context, props_cam):
        view_combinations.update_visibilities(context, self)
        properties.ARK_Camera.update_exposure(props_cam, context)
        properties.ARK_Camera.update_resolution(props_cam, context)
        return None

class ARK_OT_AddCamera(bpy.types.Operator):
    bl_idname = f"{addon.name}.add_camera"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        preferences = addon.preferences
        blcol_cameras = utils.bpy.col.obt(preferences.container_cameras)

        name = preferences.default_name
        bldata = utils.bpy.obt(bpy.data.cameras, name, force=True, overwrite='NEW')
        blcam =  utils.bpy.obj.obt(
            name,
            data=bldata,
            force=True,
            parent=blcol_cameras,
            overwrite='NEW',
        )

        bpy.ops.ark.set_camera_active(name=blcam.name)
        bpy.ops.ark.add_cam_hierarchy()
        return {'FINISHED'}

class ARK_OT_DuplicateCamera(bpy.types.Operator):
    bl_idname = f"{addon.name}.duplicate_camera"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        ao = context.active_object
        return ao is not None and ao.type == 'CAMERA' and ao.select_get()

    def execute(self, context):
        preferences = addon.preferences
        blcol_cameras = utils.bpy.col.obt(preferences.container_cameras)
        blcam = context.active_object

        new_cam = blcam.copy()
        new_cam.data = blcam.data.copy()
        view_combinations.CollectionHierarchy.cleanse_refs(new_cam)

        blcol_cameras.objects.link(new_cam)

        bpy.ops.ark.set_camera_active(name=new_cam.name)
        bpy.ops.ark.add_cam_hierarchy()
        return {'FINISHED'}

class ARK_OT_RemoveCamera(bpy.types.Operator):
    bl_idname = f"{addon.name}.remove_camera"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        ao = context.active_object
        return ao is not None and ao.type == 'CAMERA' and ao.select_get()

    def execute(self, context):
        preferences = addon.preferences
        blcam = context.active_object

        if view_combinations.CollectionHierarchy.audit(context, blcam):
            view_combinations.CollectionHierarchy.remove(context, blcam)

        utils.bpy.obj.remove(blcam, purge_data=True)
        return {'FINISHED'}

class ARK_OT_ForceCameraVerticals(bpy.types.Operator):
    bl_idname = f"{addon.name}.force_camera_verticals"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera

    def execute(self, context):
        cam_rot = context.scene.camera.rotation_euler
        cam_rot[0] = math.radians(90)
        cam_rot[1] = math.radians(0)
        return {'FINISHED'}

class ARK_PT_PROPERTIES_Scene(bpy.types.Panel):
    bl_label = "Cameras"
    bl_idname = "ARK_PT_PROPERTIES_Scene"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    @staticmethod
    def get_cam_list(container):
        if container is None:
            return None
        return [obj for obj in container.all_objects if obj.type == 'CAMERA']

    @staticmethod
    def check_cam_rotation(cam):
        conditions = [
            math.isclose(cam.rotation_euler[0], math.radians(90), rel_tol=0.1),
            math.isclose(cam.rotation_euler[1], math.radians(0), rel_tol=0.1),
        ]
        return all(conditions)

    def draw(self, context):
        layout = self.layout

        preferences = addon.preferences
        props_scene = addon.get_property("scene")
        container_cameras = utils.bpy.col.obt(preferences.container_cameras, local=True)
        cam_list = self.get_cam_list(container_cameras)
        props_cam = None

        if not container_cameras and not ArkHierarchy.audit(context):
            box = layout.box()
            row = box.row()
            row.alert = True
            row.operator(
                ARK_OT_CreateArkHierarchy.bl_idname,
                text = "Missing structure for cameras, fix it?",
            )
            return None
        else:
            box = layout.box()
            row = box.row()
            row.template_list(
                    "ARK_UL_PROPERTIES_CameraList",
                    "Camera List",
                    container_cameras,
                    "all_objects",
                    props_scene,
                    "uilist_index",
                )
            col = row.column(align=True)
            col.operator(ARK_OT_AddCamera.bl_idname, text="", icon='ADD')
            col.operator(ARK_OT_RemoveCamera.bl_idname, text="", icon='REMOVE')
            col.operator(ARK_OT_DuplicateCamera.bl_idname, text="", icon='DUPLICATE')

        blcam = context.scene.camera
        if not cam_list:
            row = box.row()
            utils.bpy.ui.alert(row, text=f"No camera in {container_cameras.name}.")
            return None
        elif not blcam:
            row = box.row(align=True)
            utils.bpy.ui.label(row, text="No active camera.")
            return None
        elif not view_combinations.CollectionHierarchy.audit(context, blcam):
            renamed = view_combinations.CollectionHierarchy.audit_previous(context, blcam)
            text = "%s" % "Camera was renamed, sync hierarchy?" if renamed else "Missing camera hierarchy, fix it?"
            row = box.row()
            row.alert = True
            row.operator(
                ARK_OT_AddCameraHierarchy.bl_idname,
                text = text,
            ).renamed = renamed
        else:
            box.row().label(text="")

        props_cam = getattr(blcam.data, addon.name)
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(props_cam, "resolution_orientation", expand=True)
        row = col.row(align=True)
        row.prop(props_cam, "ratio_x")
        row.prop(props_cam, "ratio_y")
        col.prop(props_cam, "resolution_value")
        col.prop(
            props_cam,
            "resolution_mode",
            toggle = True,
            text = "%s" % "Long Edge Resolution" if props_cam.resolution_mode else "Short Edge Resolution",
        )
        row = col.row()
        row.enabled = False
        row.label(text=f"Final Resolution: {context.scene.render.resolution_x}x{context.scene.render.resolution_y}")

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene.camera.data, "clip_start", slider=True)
        row.prop(context.scene.camera.data, "clip_end", slider=True)
        row = col.row(align=True)
        row.prop(context.scene.camera.data, "shift_x", slider=True)
        row.prop(context.scene.camera.data, "shift_y", slider=True)

        col = box.column(align=True)
        row = col.row()
        row.prop(props_cam, "projection")
        row = col.row()
        match props_cam.projection:
            case 'PERSP':
                col.prop(context.scene.camera.data, "lens")
            case 'ORTHO':
                col.prop(context.scene.camera.data, "ortho_scale")
            case _:
                pass
        row = col.row()
        if self.check_cam_rotation(context.scene.camera):
            utils.bpy.ui.label(row, text="Camera is vertical.", depress=True)
        else:
            row.alert = True
            row.operator(
                ARK_OT_ForceCameraVerticals.bl_idname,
                text = "Camera is not vertical.",
            )

        col = box.column(align=True)
        row = col.row()
        row.prop(props_cam, "exposure_mode", expand=True)
        match props_cam.exposure_mode:
            case 'EV':
                col.prop(props_cam, "ev", slider=True)
            case 'MANUAL':
                col.prop(props_cam, "aperture")
                col.prop(props_cam, "shutter_speed")
                col.prop(props_cam, "iso")
        return None

class ARK_UL_PROPERTIES_CameraList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        row.prop(bpy.data.objects[item.name], "name", text="")

        op = row.operator(
            utils.bpy.ops.UTILS_OT_Select.bl_idname,
            text="",
            icon='%s' % 'RESTRICT_SELECT_OFF' if item.select_get() or item.parent is not None and item.parent.select_get() else 'RESTRICT_SELECT_ON',
            depress= context.active_object == item and item.select_get(),
        )
        op.obj_name = item.name
        op.parent_instead = True

        op = row.operator(
            ARK_OT_SetCameraActive.bl_idname,
            text="",
            icon='%s' % 'RESTRICT_RENDER_OFF' if context.scene.camera == item else 'RESTRICT_RENDER_ON' ,
        )
        op.name=item.name
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
class ARK_Scene_Interface_Cameras(bpy.types.PropertyGroup):
    # NOTE: This index is just to fulfill call requirements,
    ## it's not used in the UIList to search for properties.
    uilist_index : bpy.props.IntProperty(
        name="",
        default=999,
    )

@addon.property
class ARK_WindowManager_Cameras(bpy.types.PropertyGroup):
    pass

@addon.property
class ARK_Preferences_Cameras(bpy.types.PropertyGroup):
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

def Preferences_UI(preferences, layout):
    box = layout.box()
    box.prop(preferences, "container_cameras")
    box.prop(preferences, "container_props")
    box.prop(preferences, "container_blockouts")
    box.prop(preferences, "trackers_camera")
    return None

CLASSES = [
    ARK_OT_CreateArkHierarchy,
    ARK_OT_AddCameraHierarchy,
    ARK_OT_SetCameraActive,
    ARK_OT_AddCamera,
    ARK_OT_DuplicateCamera,
    ARK_OT_RemoveCamera,
    ARK_OT_ForceCameraVerticals,
    ARK_WindowManager_Cameras,
    ARK_Preferences_Cameras,
    ARK_Scene_Interface_Cameras,
    ARK_PT_PROPERTIES_Scene,
    ARK_UL_PROPERTIES_CameraList,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    utils.bpy.unregister_modules(MODULES)
    return None
