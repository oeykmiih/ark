# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import utils
addon = utils.bpy.Addon()

class World(bpy.types.PropertyGroup):
    kind : bpy.props.EnumProperty(
        name = "kind",
        description = "kind",
        items = [
            ('NONE', "NONE", ""),
            ('SKY', "SKY", ""),
            ('HDRI', "HDRI", ""),
        ],
        default = 'NONE',
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