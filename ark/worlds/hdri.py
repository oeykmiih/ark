# SPDX-License-Identifier: GPL-2.0-or-later
import os
import glob
import json

import bpy
import bpy.utils.previews

from ark import utils
addon = utils.bpy.Addon()

global bl_previews

SUPPORTED_FORMATS = {".hdr", ".exr"}

def audit_library():
    return os.path.exists(bpy.path.abspath(addon.preferences.library))

def reload_thumbnails(generate=False, force=False):
    library = bpy.path.abspath(addon.preferences.library)
    lib_thumbnails = bpy.path.abspath(addon.preferences.lib_thumbnails)

    hdris = {os.path.basename(p) : p for p in glob.glob(os.path.join(library, "**"), recursive=True) if os.path.splitext(p)[1] in SUPPORTED_FORMATS}
    _thumbnails = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(lib_thumbnails, "*.jpg"))}
    _hdris = set(hdris.keys())

    to_remove = _thumbnails.difference(_hdris)
    for name in to_remove:
        print("DELETING: ", name)
        os.remove(os.path.join(lib_thumbnails, name + ".jpg"))

    thumbnails = list(_thumbnails.difference(to_remove))
    if generate:
        to_generate = _hdris.difference(_thumbnails) if force == False else hdris

        for name in to_generate:
            print("GENERATING: ", name)
            thumbnails.append(
                utils.bpy.img.generate_thumbnail(hdris[name], os.path.join(lib_thumbnails, name + ".jpg"))
            )

    addon.session.hdris = json.dumps(hdris)
    return thumbnails

def enum_previews(self, context):
    lib_thumbnails = bpy.path.abspath(addon.preferences.lib_thumbnails)
    return load_previews({p for p in glob.glob(os.path.join(lib_thumbnails, "*.jpg"))})

def load_previews(thumbnails):
    global bl_previews

    enum_items = []

    i = 0
    for fp in thumbnails:
        fn = os.path.basename(fp)
        name = os.path.splitext(fn)[0]

        icon = bl_previews.get(fn)
        if icon is None:
            thumb = bl_previews.load(fn, fp, 'IMAGE')
        else:
            thumb = bl_previews[fn]

        enum_items.append((name, name, "", thumb.icon_id, i))
        i +=1

    if len(enum_items) == 0:
        pass
    return enum_items

def reload_previews(generate=False, force=False):
    load_previews(reload_thumbnails(generate=generate, force=force))
    return None

def audit_hdri():
    return get_hdri(addon.preferences, addon.session)

def get_hdri(preferences, session):
    reload_previews(force=True)
    hdris = json.loads(session.hdris)
    if session.preview in hdris:
        path = hdris[session.preview]
        if os.path.exists(path):
            return (os.path.basename(path), path)
        else:
            return False
    else:
        return False

def get_tex(context, file):
    if file[0] in context.blend_data.images:
        tex = context.blend_data.images[file[0]]
    else:
        tex = context.blend_data.images.load(file[1])
    return tex

def handle_existing_world(world):
    session = addon.session
    w_nodes = world.node_tree.nodes
    if "hdri.env" in w_nodes and w_nodes["hdri.env"].image is not None:
        existing = w_nodes["hdri.env"].image.name
        if existing != session.preview:
            if existing in reload_thumbnails():
                session.preview = existing
    return None

def apply_world(world, tex):
    world.node_tree.nodes["hdri.env"].image = tex
    return None

def update_world(self, context):
    world = context.scene.world
    pr_world = getattr(world, addon.name)

    setup_world(world)
    reload_thumbnails()

    if pr_world.kind == 'HDRI':
        preferences = addon.preferences
        session = addon.session

        file = get_hdri(preferences, session)
        if file:
            tex = get_tex(context, file)
            apply_world(world, tex)
        else:
            pass

        reload_previews()
    return None

def audit_world(world):
    return "hdri.env" in  world.node_tree.nodes

def setup_world(world):
    world.use_nodes = True
    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links

    n_coord = w_nodes["hdri.coord"] if "hdri.coord" in w_nodes else w_nodes.new('ShaderNodeTexCoord')
    n_coord.label = n_coord.name = "hdri.coord"
    n_coord.location = (-700,-200)

    n_mapping = w_nodes["hdri.mapping"] if "hdri.mapping" in w_nodes else w_nodes.new('ShaderNodeMapping')
    n_mapping.label = n_mapping.name = "hdri.mapping"
    n_mapping.location = (-500, -200)
    w_links.new(n_coord.outputs[0], n_mapping.inputs['Vector'])

    n_env = w_nodes["hdri.env"] if "hdri.env" in w_nodes else w_nodes.new('ShaderNodeTexEnvironment')
    n_env.label = n_env.name = "hdri.env"
    n_env.location = (-300, -200)
    w_links.new(n_mapping.outputs[0], n_env.inputs[0])

    n_background = w_nodes["hdri.background"] if "hdri.background" in w_nodes else w_nodes.new('ShaderNodeBackground')
    n_background.label = n_background.name = "hdri.background"
    n_background.location = (0, -200)
    w_links.new(n_env.outputs[0], n_background.inputs[0])

    n_output = w_nodes["hdri.output"] if "hdri.output" in w_nodes else w_nodes.new('ShaderNodeOutputWorld')
    n_output.label = n_output.name = "hdri.output"
    n_output.location = (200, -200)
    n_output.is_active_output = True
    w_links.new(n_background.outputs[0], n_output.inputs[0])
    return None

def create_world(world, context):
    pr_world = getattr(world, addon.name)
    setup_world(world)
    pr_world.kind = 'HDRI'
    if audit_library():
        hdri = audit_hdri()
        if hdri:
            apply_world(world, get_tex(context, hdri))
    pr_world.active = True
    return None

def get_mapping(world):
    return world.node_tree.nodes["hdri.mapping"].inputs[2]

class ARK_OT_ReloadHDRIPreviews(bpy.types.Operator):
    bl_idname = f"{addon.name}.reload_previews"
    bl_label = ""
    bl_options = {'INTERNAL'}

    shift : bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return audit_library() != 'NONE'

    def invoke(self, context, event):
        self.shift = event.shift
        return self.execute(context)

    def execute(self, context):
        reload_previews(generate=True, force=self.shift)
        return {'INTERFACE'}

class ARK_OT_CreateWorldHDRI(bpy.types.Operator):
    bl_idname = f"{addon.name}.create_world_hdri"
    bl_label = ""

    def execute(self, context):
        world = context.scene.world
        create_world(world, context)
        return {'FINISHED'}

@addon.property
class WindowManager_Worlds_HDRI(bpy.types.PropertyGroup):
    preview : bpy.props.EnumProperty(
        items = enum_previews,
        update = update_world,
    )

    hdris : bpy.props.StringProperty()

@addon.property
class Preferences_Worlds_HDRI(bpy.types.PropertyGroup):
    def update_library(self, context):
        self.lib_thumbnails = os.path.join(self.library, "_thumbnails")
        return None

    library : bpy.props.StringProperty(
        name = "Library Path",
        default = "",
        description = "Folder where you store your HDRI images for the World Environment",
        subtype = 'DIR_PATH',
        update = update_library,
    )

    lib_thumbnails : bpy.props.StringProperty(
        name = "Path for Library Thumbnails",
        default = "",
        subtype = 'DIR_PATH',
    )

def UI(preferences, layout):
    layout.prop(preferences, "library")
    return None

CLASSES = [
    ARK_OT_ReloadHDRIPreviews,
    ARK_OT_CreateWorldHDRI,
    WindowManager_Worlds_HDRI,
    Preferences_Worlds_HDRI,
]

def register():
    utils.bpy.register_classes(CLASSES)

    global bl_previews
    bl_previews = bpy.utils.previews.new()
    return None

def unregister():
    global bl_previews
    bl_previews = bpy.utils.previews.remove(bl_previews)

    utils.bpy.unregister_classes(CLASSES)
    return None