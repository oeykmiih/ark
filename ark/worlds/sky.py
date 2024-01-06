# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from ark import utils
addon = utils.bpy.Addon()

def get_env_node(world):
    return world.node_tree.nodes["sky.env"]

def create_world(world, context):
    pr_world = getattr(world, addon.name)
    setup_world(world)
    pr_world.kind = 'SKY'
    pr_world.active = True
    return None

def audit_world(world):
    return "sky.env" in  world.node_tree.nodes and not world.node_tree.nodes["sky.env"].mute

def setup_world(world):
    world.use_nodes = True
    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links

    _ = [True]*len(w_nodes)
    w_nodes.foreach_set("mute", _)

    n_env = w_nodes["sky.env"] if "sky.env" in w_nodes else w_nodes.new('ShaderNodeTexSky')
    n_env.label = n_env.name = "sky.env"
    n_env.location = (-200, 200)
    n_env.mute = False

    n_background = w_nodes["sky.background"] if "sky.background" in w_nodes else w_nodes.new('ShaderNodeBackground')
    n_background.label = n_background.name = "sky.background"
    n_background.location = (0, 200)
    n_background.mute = False
    w_links.new(n_env.outputs[0], n_background.inputs[0])

    n_output = w_nodes["sky.output"] if "sky.output" in w_nodes else w_nodes.new('ShaderNodeOutputWorld')
    n_output.label = n_output.name = "sky.output"
    n_output.location = (200, 200)
    n_output.mute = False
    n_output.is_active_output = True
    w_links.new(n_background.outputs[0], n_output.inputs[0])

    pr_world = getattr(world, addon.name)
    pr_world.sun_position.sky_texture = n_env.name
    return None

class ARK_OT_CreateWorldSky(bpy.types.Operator):
    bl_idname = f"{addon.name}.create_world_sky"
    bl_label = ""

    def execute(self, context):
        world = context.scene.world
        create_world(world, context)
        return {'FINISHED'}

@addon.property
class WindowManager_Worlds_Sky(bpy.types.PropertyGroup):
    pass
@addon.property
class Preferences_Worlds_Sky(bpy.types.PropertyGroup):
    pass

def UI(preferences, layout):
    return None

CLASSES = [
    ARK_OT_CreateWorldSky,
    WindowManager_Worlds_Sky,
    Preferences_Worlds_Sky,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None