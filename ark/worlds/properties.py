# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
addon = utils.bpy.Addon()

from . import enums
from . import sun_position
from . import hdri
from . import sky

class World(bpy.types.PropertyGroup):
    sun_position : bpy.props.PointerProperty(type=sun_position.World_SunPosition)

    active : bpy.props.BoolProperty()

    def update_kind(self, context):
        match self.kind:
            case 'HDRI':
                hdri.setup_world(context.scene.world)
            case 'SKY':
                sky.setup_world(context.scene.world)
        return None

    kind : bpy.props.EnumProperty(
        name = "kind",
        description = "kind",
        items = enums.WORLD_KIND,
        default = enums.WORLD_KIND[1][0],
        update = update_kind,
    )

CLASSES = [
    World,
]

PROPS = [
    World,
]

def register():
    utils.bpy.register_classes(CLASSES)
    addon.set_properties(PROPS)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None