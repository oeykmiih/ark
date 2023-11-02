# SPDX-License-Identifier: GPL-2.0-or-later
import math

import bpy
from ark import utils
addon = utils.bpy.Addon()

from . import defaults
from . import enums

class Camera_Hierarchy(bpy.types.PropertyGroup):
    blockouts : bpy.props.StringProperty()
    props : bpy.props.StringProperty()

class Camera(bpy.types.PropertyGroup):
    hierarchy : bpy.props.PointerProperty(type=Camera_Hierarchy)

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
        update = update_exposure,
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

    render : bpy.props.BoolProperty(
        name = "",
        description = "Include in RenderQueue",
        default = False,
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

CLASSES = [
    Camera_Hierarchy,
    Camera,
]

PROPS = [
    Camera,
]

def register():
    utils.bpy.register_classes(CLASSES)
    addon.set_properties(PROPS)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
