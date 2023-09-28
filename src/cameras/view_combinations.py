# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

import utils
addon = utils.bpy.Addon()

def update_visibilities(context, blcam):
    update_collection_hierarchy(context, blcam)
    return None

def update_collection_hierarchy(context, blcam):
    preferences = addon.parent_preferences
    containers = {}
    containers["props"] = preferences.container_props
    containers["blockouts"] = preferences.container_blockouts
    exempt = [
        f"PR:{blcam.name}",
        f"BK:{blcam.name}",
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

    if utils.bpy.col.obt(f"BK:{blcam.name}") is not None:
        for blob in utils.bpy.col.obt(f"BK:{blcam.name}").objects:
            blob.visible_camera = False
            blob.visible_diffuse = False
            blob.visible_glossy = False
            blob.visible_transmission = False
            blob.visible_volume_scatter = False
    return None

class CollectionHierarchy():
    @staticmethod
    def create(context, blcam=None):
        preferences = addon.parent_preferences
        name = blcam.name

        blcol_blockouts = utils.bpy.col.obt(preferences.container_blockouts, force=True)
        utils.bpy.col.obt(f"BK:{name}", force=True, parent=blcol_blockouts)
        blcol_props = utils.bpy.col.obt(preferences.container_props, force=True)
        utils.bpy.col.obt(f"PR:{name}", force=True, parent=blcol_props)
        return None

    @staticmethod
    def update(context, blcam=None):
        preferences = addon.parent_preferences
        name = blcam.name
        props_cam = getattr(blcam.data, addon.name)

        blcol_blockouts = utils.bpy.col.obt(preferences.container_blockouts, force=True)
        cam_blockouts = utils.bpy.col.obt(props_cam.hierarchy.blockouts, parent=blcol_blockouts)
        blcol_props = utils.bpy.col.obt(preferences.container_props, force=True)
        cam_props = utils.bpy.col.obt(props_cam.hierarchy.props, parent=blcol_props)

        cam_blockouts.name = f"BK:{name}"
        cam_props.name = f"PR:{name}"
        return None

    @staticmethod
    def remove(context, blcam=None):
        preferences = addon.parent_preferences
        name = blcam.name

        blcol_blockouts = utils.bpy.col.obt(preferences.container_blockouts, force=True)
        cam_blockouts = utils.bpy.col.obt(f"BK:{name}", local=True)
        blcol_props = utils.bpy.col.obt(preferences.container_props, force=True)
        cam_props = utils.bpy.col.obt(f"PR:{name}", local=True)

        utils.bpy.col.empty(cam_blockouts, objects=True)
        blcol_blockouts.children.unlink(cam_blockouts)
        utils.bpy.col.empty(cam_props, objects=True)
        blcol_props.children.unlink(cam_props)
        return None

    @staticmethod
    def audit(context, blcam=None):
        preferences = addon.parent_preferences
        name = blcam.name

        conditions = [
            utils.bpy.col.obt(preferences.container_blockouts),
            utils.bpy.col.obt(f"BK:{name}", local=True),
            utils.bpy.col.obt(preferences.container_props),
            utils.bpy.col.obt(f"PR:{name}", local=True),
        ]
        return all(conditions)

    @staticmethod
    def audit_previous(context, blcam=None):
        preferences = addon.parent_preferences
        props_cam = getattr(blcam.data, addon.name)
        conditions = [
            utils.bpy.col.obt(preferences.container_blockouts),
            utils.bpy.col.obt(props_cam.hierarchy.blockouts, local=True),
            utils.bpy.col.obt(preferences.container_props),
            utils.bpy.col.obt(props_cam.hierarchy.props, local=True),
        ]
        return all(conditions)

    @staticmethod
    def save_refs(context, blcam=None):
        props_cam = getattr(blcam.data, addon.name)
        props_cam.hierarchy.blockouts = f"BK:{context.scene.camera.name}"
        props_cam.hierarchy.props = f"PR:{context.scene.camera.name}"
        return None

    @staticmethod
    def cleanse_refs(blcam):
        props_cam = getattr(blcam.data, addon.name)
        props_cam.hierarchy.blockouts = ""
        props_cam.hierarchy.props = ""
        return None

@addon.property
class ARK_WindowManager_Cameras_ViewCombinations(bpy.types.PropertyGroup):
    pass

@addon.property
class ARK_Preferences_Cameras_ViewCombinations(bpy.types.PropertyGroup):
    pass

def Preferences_UI(preferences, layout):
    items = (name for name, module in MODULES.items() if hasattr(module, "Preferences_UI"))
    for name in items:
        module = MODULES[name]
        properties = getattr(preferences, name)
        layout = layout.box()
        module.Preferences_UI(properties, layout)
    return None

CLASSES = [
    ARK_WindowManager_Cameras_ViewCombinations,
    ARK_Preferences_Cameras_ViewCombinations,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
