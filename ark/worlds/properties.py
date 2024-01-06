# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
addon = utils.bpy.Addon()

from . import enums
class World(bpy.types.PropertyGroup):
    created : bpy.props.BoolProperty()
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