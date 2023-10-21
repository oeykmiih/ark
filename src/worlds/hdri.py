# SPDX-License-Identifier: GPL-2.0-or-later
import os
import glob

import bpy
import utils
addon = utils.bpy.Addon()

global bl_previews

SUPPORTED_FORMATS = {".hdr", ".exr"}

def audit_library():
    return os.path.exists(bpy.path.abspath(addon.preferences.library))

def reload_thumbnails(force=False):
    library = bpy.path.abspath(addon.preferences.library)
    library_thumbnails = os.path.join(library, "_thumbnails")
    thumbnails = {os.path.splitext(fn)[0] for fn in os.listdir(library_thumbnails) if fn.lower().endswith(".jpg")}
    _hdris = {os.path.splitext(fn)[0] : os.path.join(library, fn) for fn in os.listdir(library) if os.path.splitext(fn)[1] in SUPPORTED_FORMATS}

    hdris = set(_hdris.keys())
    to_remove = thumbnails.difference(hdris)
    to_generate = hdris.difference(thumbnails) if force == False else hdris
    thumbnails = []

    for name in to_remove:
        os.remove(os.path.join(library_thumbnails, name + ".jpg"))
        print("DELETING: ", name)

    for name in to_generate:
        print("GENERATING: ", name)
        thumbnails.append(
            utils.bpy.img.generate_thumbnail(_hdris[name], os.path.join(library_thumbnails, name + ".jpg"))
        )

    return thumbnails

def enum_previews(self, context):
    library_thumbnails = os.path.join(bpy.path.abspath(addon.preferences.library), "_thumbnails")
    items = [os.path.join(library_thumbnails, fn) for fn in os.listdir(library_thumbnails) if fn.lower().endswith(".jpg")]
    return load_previews(items)

def load_previews(thumbnails):
    library = os.path.join(bpy.path.abspath(addon.preferences.library), "_thumbnails")
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

def reload_previews(force=False):
    load_previews(reload_thumbnails(force=force))
    return None

def audit_hdri():
    return get_hdri(addon.preferences, addon.session)

def get_hdri(preferences, session):
    for path in glob.glob(os.path.join(bpy.path.abspath(preferences.library), session.previews + ".*")):
            if os.path.splitext(path)[1] in SUPPORTED_FORMATS:
                result = (os.path.basename(path), path)
                break
    else:
        result = False
    return result

def get_tex(context,  paths):
    if paths[0] in context.blend_data.images:
        tex = context.blend_data.images[paths[0]]
    else:
        tex = context.blend_data.images.load(paths[1])
    return tex

def apply_world_hdri(world, tex):
    world.node_tree.nodes["HDRI"].image = tex
    return None

def update_world_hdri(self, context):
    world = context.scene.world
    pr_world = getattr(world, addon.name)

    if pr_world.kind == 'HDRI':
        preferences = addon.preferences
        session = addon.session

        paths = get_hdri(preferences, session)
        if paths:
            tex = get_tex(context, paths)
            apply_world_hdri(world, tex)

        reload_previews()
    return None

def setup_world_hdri(world):
    world.use_nodes = True
    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links

    n_coord = w_nodes["Texture Coordinates"] if "Texture Coordinates" in w_nodes else w_nodes.new('ShaderNodeTexCoord')
    n_coord.location = (-700,-200)

    n_mapping = w_nodes["Mapping"] if "Mapping" in w_nodes else w_nodes.new('ShaderNodeMapping')
    n_mapping.location = (-500, -200)
    w_links.new(n_coord.outputs[0], n_mapping.inputs['Vector'])

    n_tex = w_nodes["HDRI"] if "HDRI" in w_nodes else w_nodes.new('ShaderNodeTexEnvironment')
    n_tex.name = "HDRI"
    n_tex.location = (-300, -200)
    w_links.new(n_mapping.outputs[0], n_tex.inputs[0])

    n_background = w_nodes["Background"] if "Background" in w_nodes else w_nodes.new('ShaderNodeBackground')
    n_background.location = (0, -200)
    w_links.new(n_tex.outputs[0], n_background.inputs[0])

    n_output = w_nodes['World Output'] if "Background" in w_nodes else w_nodes.new('ShaderNodeOutputWorld')
    n_output.location = (200, -200)
    w_links.new(n_background.outputs[0], n_output.inputs[0])
    return None

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
        reload_previews(force=self.shift)
        return {'INTERFACE'}

class ARK_OT_CreateWorldHDRI(bpy.types.Operator):
    bl_idname = f"{addon.name}.create_world_hdri"
    bl_label = ""

    def execute(self, context):
        session = addon.session
        world = context.scene.world
        pr_world = getattr(world, addon.name)
        setup_world_hdri(world)
        pr_world.kind = 'HDRI'
        if audit_library():
            hdri = audit_hdri()
            if hdri:
                apply_world_hdri(world, get_tex(context, hdri))
        return {'FINISHED'}

@addon.property
class WindowManager_Worlds_HDRI(bpy.types.PropertyGroup):
    previews : bpy.props.EnumProperty(
        items = enum_previews,
        update = update_world_hdri,
    )

@addon.property
class Preferences_Worlds_HDRI(bpy.types.PropertyGroup):
    library: bpy.props.StringProperty(
        name = "Library Path",
        default = "",
        description = "Folder where you store your HDRI images for the World Environment",
        subtype = "DIR_PATH",
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

    import bpy.utils.previews
    global bl_previews
    bl_previews = bpy.utils.previews.new()
    return None

def unregister():
    global bl_previews
    bl_previews = bpy.utils.previews.remove(bl_previews)

    utils.bpy.unregister_classes(CLASSES)
    return None