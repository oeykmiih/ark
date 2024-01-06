# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
addon = utils.bpy.Addon()

def get_background_node(world):
    for node in world.node_tree.nodes:
        if node.bl_idname == 'ShaderNodeOutputWorld':
            if node.is_active_output:
                if len(node.inputs[0].links) == 0:
                    return None
                else:
                    found = node.inputs[0].links[0].from_node
                    return found if found.bl_idname == 'ShaderNodeBackground' else None

def get_world_strength(world):
    node = get_background_node(world)
    return node.inputs[1]

def ligth_stop(bl_prop, key, factor):
    setattr(bl_prop, key, getattr(bl_prop, key) * pow(2, factor))
    return None

STOP_MODES = [
    "WORLD",
    "NODE",
]

class ARK_OT_SubLightStop(bpy.types.Operator):
    bl_idname = f"{addon.name}.worlds_lightstop_subtract"
    bl_label = ""
    bl_options = {'INTERNAL'}

    mode : bpy.props.EnumProperty(
        name = "mode",
        description = "mode",
        items = utils.bpy.enum_from_list(STOP_MODES, raw=True),
    )
    factor : bpy.props.FloatProperty(default=-0.5)
    world : bpy.props.StringProperty()
    material : bpy.props.StringProperty()
    node : bpy.props.StringProperty()

    @staticmethod
    def button(self, context):
        self.layout.operator(ARK_OT_SubLightStop.bl_idname, icon='REMOVE')
        return None

    def execute(self, context):
        match self.mode:
            case 'WORLD':
                ligth_stop(get_world_strength(bpy.data.worlds[self.world]), "default_value", self.factor)
            case 'NODE':
                pass
        return {'FINISHED'}

class ARK_OT_AddLightStop(bpy.types.Operator):
    bl_idname = f"{addon.name}.worlds_lightstop_add"
    bl_label = ""
    bl_options = {'INTERNAL'}

    mode : bpy.props.EnumProperty(
        name = "mode",
        description = "mode",
        items = utils.bpy.enum_from_list(STOP_MODES, raw=True),
    )
    factor : bpy.props.FloatProperty(default=0.5)
    world : bpy.props.StringProperty()
    material : bpy.props.StringProperty()
    node : bpy.props.StringProperty()

    @staticmethod
    def button(self, context):
        self.layout.operator(ARK_OT_AddLightStop.bl_idname, icon='ADD')
        return None

    def execute(self, context):
        match self.mode:
            case 'WORLD':
                ligth_stop(get_world_strength(bpy.data.worlds[self.world]), "default_value", self.factor)
            case 'NODE':
                pass
        return {'FINISHED'}

CLASSES = [
    ARK_OT_AddLightStop,
    ARK_OT_SubLightStop,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
