# SPDX-License-Identifier: GPL-2.0-or-later
import importlib
import math
import bpy

from .. import addon
from .. import utils

from . import enums
from . import defaults

class ARK_OT_CreateArkHierachy(bpy.types.Operator):
    """ARK Operator to set active camera."""
    bl_idname = f"{addon.name}.create_ark_hierarchy"
    bl_label = ""
    bl_options = {'UNDO' , 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.create_ark_hierarchy(context)
        return {'FINISHED'}

    @staticmethod
    def create_ark_hierarchy(context):
        preferences = addon.preferences().cameras
        blcol_cameras = utils.blcol.obt(preferences.container_cameras, force=True, parent=context.scene.collection)
        blcol_blockouts = utils.blcol.obt(preferences.container_blockouts, force=True, parent=context.scene.collection)
        blcol_props = utils.blcol.obt(preferences.container_props, force=True, parent=context.scene.collection)
        return None

    @staticmethod
    def check_ark_hierarchy(context):
        preferences = addon.preferences().cameras
        conditions = [
            utils.blcol.obt(preferences.container_blockouts, local=True),
            utils.blcol.obt(preferences.container_props, local=True),
        ]
        return all(conditions)

class ARK_OT_CreateCamHierachy(bpy.types.Operator):
    """ARK Operator to set active camera."""
    bl_idname = f"{addon.name}.create_cam_hierarchy"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.create_cam_hierarchy(context)
        return {'FINISHED'}

    @staticmethod
    def create_cam_hierarchy(context):
        preferences = addon.preferences().cameras
        blcol_props = utils.blcol.obt(preferences.container_props, force=True)
        utils.blcol.obt(f"PR:{context.scene.camera.name}", force=True, parent=blcol_props)
        blcol_blockouts = utils.blcol.obt(preferences.container_blockouts, force=True)
        utils.blcol.obt(f"BK:{context.scene.camera.name}", force=True, parent=blcol_blockouts)
        return

    @staticmethod
    def check_cam_hierarchy(context):
        preferences = addon.preferences().cameras
        conditions = [
            utils.blcol.obt(preferences.container_props),
            utils.blcol.obt(f"PR:{context.scene.camera.name}", local=True),
            utils.blcol.obt(preferences.container_blockouts),
            utils.blcol.obt(f"BK:{context.scene.camera.name}", local=True),
        ]
        return all(conditions)

class ARK_OT_SetCameraActive(bpy.types.Operator):
    """ARK Operator to set active camera."""
    bl_idname = f"{addon.name}.set_camera_active"
    bl_label = ""
    bl_options = {'UNDO', 'INTERNAL'}

    name: bpy.props.StringProperty()

    def execute(self, context):
        preferences = addon.preferences().cameras
        cam = context.scene.camera = bpy.data.objects.get(self.name)
        props_cam = eval(f"context.scene.camera.data.{addon.name}")
        blcol_cameras = utils.blcol.obt(preferences.container_cameras, local=True)

        tracker = utils.blob.obt(preferences.trackers_camera, parent=blcol_cameras, force=True, local=True)
        tracker.matrix_world = cam.matrix_world
        tracker.use_fake_user = True
        tracker.hide_select = True
        tracker.hide_viewport = True

        self.update_cam_properties(context, props_cam)
        return {'FINISHED'}

    def update_cam_properties(self, context, props_cam):
        self.update_visibilities(context)
        ARK_PROPS_Camera.update_exposure(props_cam, context)
        ARK_PROPS_Camera.update_resolution(props_cam, context)
        return None

    def update_visibilities(self, context):
        preferences = addon.preferences().cameras
        containers = {}
        containers["props"] = preferences.container_props
        containers["blockouts"] = preferences.container_blockouts
        exempt = [
            f"PR:{self.name}",
            f"BK:{self.name}",
            ]

        for bl_layer_collection in context.view_layer.layer_collection.children[containers["props"]].children:
            if bl_layer_collection.name not in exempt:
                bl_layer_collection.exclude = True
            else:
                bl_layer_collection.exclude = False

        for bl_layer_collection in context.view_layer.layer_collection.children[containers["blockouts"]].children:
            if bl_layer_collection.name not in exempt:
                bl_layer_collection.exclude = True
            else:
                bl_layer_collection.exclude = False

        if utils.blcol.obt(f"BK:{self.name}") is not None:
            for blob in utils.blcol.obt(f"BK:{self.name}").objects:
                blob.visible_camera = False
                blob.visible_diffuse = False
                blob.visible_glossy = False
                blob.visible_transmission = False
                blob.visible_volume_scatter = False
        return None

class ARK_OT_ForceCameraVerticals(bpy.types.Operator):
    """ARK Operator to force 2 point perspective."""
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

class ARK_PROPS_Camera(bpy.types.PropertyGroup):
    """ARK Camera Properties"""
    def set_aperture(self, value):
        self["aperture"] = value
        self.update_exposure(bpy.context)
        self.update_aperture(bpy.context)
        return None

    def get_aperture(self):
        default = defaults.APERTURE
        index = [i for i, tupl in enumerate(enums.APERTURE) if tupl[0] == default][0]
        return self.get("aperture", index)

    def update_aperture(self, context):
        if context.scene.camera.data.dof.use_dof:
            context.scene.camera.data.dof.aperture_fstop = float(self.aperture) * context.scene.unit_settings.scale_length
        return None

    aperture : bpy.props.EnumProperty(
        name = "Aperture",
        description = "",
        items = enums.APERTURE,
        set = set_aperture,
        get = get_aperture,
    )

    def set_ev(self, value):
        self["ev"] = value
        self.update_exposure(bpy.context)
        return None

    def get_ev(self):
        default = defaults.EV
        return self.get("ev", default)

    def calculate_ev(self, context):
        A = float(self.aperture)
        S = 1/float(self.shutter_speed)
        I = float(self.iso)
        return round(math.log((A*A*100)/(S*I),2))

    ev : bpy.props.FloatProperty(
        name = "Exposure Value",
        description = "Exposure Value",
        soft_min = -6,
        soft_max = 19,
        step = 1,
        precision = 2,
        set = set_ev,
        get = get_ev,
    )

    def update_exposure(self, context):
        match self.exposure_mode:
            case 'EV':
                ev = self.ev
            case 'MANUAL':
                ev = self.calculate_ev(context)
            case _:
                pass
        bl_exposure = (ev * -1) + 11.5
        context.scene.view_settings.exposure = bl_exposure
        return None

    exposure_mode : bpy.props.EnumProperty(
        name = "Exposure Mode",
        description = "",
        items = enums.EXPOSURE_MODE,
        options = {'HIDDEN'},
        update = update_exposure
    )

    def set_iso(self, value):
        self["iso"] = value
        self.update_exposure(bpy.context)
        return None

    def get_iso(self):
        default = defaults.ISO
        index = [i for i, tupl in enumerate(enums.ISO) if tupl[0] == default][0]
        return self.get("iso", index)

    iso : bpy.props.EnumProperty(
        name = "ISO",
        description = "",
        items = enums.ISO,
        set = set_iso,
        get = get_iso,
    )

    def update_projection(self, context):
        context.scene.camera.data.type = self.projection
        return None

    projection : bpy.props.EnumProperty(
        name = "Projection",
        description = "",
        items = enums.PROJECTION,
        update = update_projection,
    )

    def update_resolution(self, context):
        if self.ratio_x > self.ratio_y:
            ratio = self.ratio_x / self.ratio_y
        else:
            ratio = self.ratio_y / self.ratio_x

        if self.resolution_mode:
            resolution_x = int(self.resolution_value)
            resolution_y = int(1 / ratio * self.resolution_value)
        else:
            resolution_x = int(ratio * self.resolution_value)
            resolution_y = int(self.resolution_value)

        match self.resolution_orientation:
            case 'PORTRAIT':
                context.scene.render.resolution_x = resolution_y
                context.scene.render.resolution_y = resolution_x
            case 'LANDSCAPE':
                context.scene.render.resolution_x = resolution_x
                context.scene.render.resolution_y = resolution_y
        return None

    ratio_x : bpy.props.FloatProperty(
        name = "Ratio X",
        description = "",
        default = defaults.RATIO_A,
        min = 0.01,
        max = 10,
        precision = 2,
        update = update_resolution,
    )

    ratio_y : bpy.props.FloatProperty(
        name = "Ratio Y",
        description = "",
        default = defaults.RATIO_B,
        min = 0.01,
        max = 10,
        precision = 2,
        update = update_resolution,
    )

    resolution_mode : bpy.props.BoolProperty(
        name = "Resolution Long Edge Mode",
        description = "",
        default = defaults.RESOLUTION_MODE,
        update = update_resolution,
    )

    resolution_orientation : bpy.props.EnumProperty(
        name = "Orientation",
        description = "",
        items = enums.RESOLUTION_ORIENTATION,
        default = defaults.RESOLUTION_ORIENTATION,
        update = update_resolution,
    )

    resolution_value : bpy.props.IntProperty(
        name = "Resolution Value",
        description = "",
        default = defaults.RESOLUTION_VALUE,
        min = 0,
        subtype = 'PIXEL',
        update = update_resolution,
    )

    def set_shutter_speed(self, value):
        self["shutter_speed"] = value
        self.update_exposure(bpy.context)
        return None

    def get_shutter_speed(self):
        default = defaults.SHUTTER_SPEED
        index = [i for i, tupl in enumerate(enums.SHUTTER_SPEED) if tupl[0] == default][0]
        return self.get("shutter_speed", index)

    shutter_speed : bpy.props.EnumProperty(
        name = "Shutter Speed",
        description = "Shutter Speed",
        items = enums.SHUTTER_SPEED,
        set = set_shutter_speed,
        get = get_shutter_speed,
    )

class ARK_PT_PROPERTIES_Scene(bpy.types.Panel):
    """ARK PANEL Scene Properties"""
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

        preferences = addon.preferences().cameras
        props_scene = addon.props("scene")
        container_cameras = utils.blcol.obt(preferences.container_cameras, local=True)
        cam_list = self.get_cam_list(container_cameras)
        props_cam = None

        if not container_cameras and not ARK_OT_CreateArkHierachy.check_ark_hierarchy(context):
            box = layout.box()
            row = box.row()
            row.alert = True
            row.operator(
                ARK_OT_CreateArkHierachy.bl_idname,
                text = "Missing structure for cameras, fix it?",
            )
        else:
            col = layout.column(align=True)
            col.template_list(
                    "ARK_UL_PROPERTIES_CameraList",
                    "Camera List",
                    container_cameras,
                    "all_objects",
                    props_scene,
                    "active_camera_index",
                )

        if not context.scene.camera:
            row = layout.row(align=True)
            row.alert=True
            utils.blui.label(row, text="No active camera.")
            row.prop(context.scene, "camera", text="")
            return None
        elif not cam_list:
            row = layout.row()
            row.operator(
                utils.UTILS_OT_Placeholder.bl_idname,
                text="Cameras must be inside {container_cameras.name} to appear.",
            )
        elif not ARK_OT_CreateCamHierachy.check_cam_hierarchy(context):
            row = layout.row()
            row.alert = True
            row.operator(
                ARK_OT_CreateCamHierachy.bl_idname,
                text = "Missing structure for active camera, fix it?",
            )
        else:
            layout.label(text="")

        props_cam = eval(f"context.scene.camera.data.{addon.name}")
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
            utils.blui.label(row, text="Camera is vertical.", depress=True)
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
    """ARK UIList Camera List"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        if context.scene.camera == item:
            row.operator(
                ARK_OT_SetCameraActive.bl_idname,
                text="",
                icon='RESTRICT_RENDER_OFF',
            ).name=item.name
        else:
            row.operator(
                ARK_OT_SetCameraActive.bl_idname,
                text="",
                icon='RESTRICT_RENDER_ON',
            ).name=item.name

        op = row.operator(
            utils.blop.UTILS_OT_Select.bl_idname,
            text="",
            icon="%s" % 'RESTRICT_SELECT_OFF' if item.select_get() or item.parent is not None and item.parent.select_get() else 'RESTRICT_SELECT_ON',
        )
        op.obj_name = item.name
        op.parent_instead = True

        row.prop(bpy.data.objects[item.name], "name", text='')
        return None

    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        filtered = []
        ordered = []
        items = getattr(data, propname)

        # Initialize with all items visible
        filtered = [self.bitflag_filter_item] * len(items)
        # Filtering out the first item
        for i, item in enumerate(items):
            if item.type != 'CAMERA':
                filtered[i] &= ~self.bitflag_filter_item

        return filtered, ordered

class ARK_PREFS_Cameras(bpy.types.PropertyGroup):
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

def ARK_PREFS_Cameras_UI(preferences, layout):
    box = layout.box()
    box.prop(preferences.cameras, "container_cameras")
    box.prop(preferences.cameras, "container_props")
    box.prop(preferences.cameras, "container_blockouts")
    box.prop(preferences.cameras, "trackers_camera")
    return None

CLASSES = [
    ARK_OT_CreateArkHierachy,
    ARK_OT_CreateCamHierachy,
    ARK_OT_SetCameraActive,
    ARK_OT_ForceCameraVerticals,
    ARK_PREFS_Cameras,
    ARK_PROPS_Camera,
    ARK_PT_PROPERTIES_Scene,
    ARK_UL_PROPERTIES_CameraList,
]

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    addon.set_props(ARK_PROPS_Camera)
    return None

def unregister():
    addon.del_props(ARK_PROPS_Camera)

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    return None
