# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
addon = utils.bpy.Addon()

class World(bpy.types.PropertyGroup):
    created : bpy.props.BoolProperty()
    kind : bpy.props.EnumProperty(
        name = "kind",
        description = "kind",
        items = [
            ('SKY', "Sky", ""),
            ('HDRI', "HDRI", ""),
        ],
        default = 'SKY',
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