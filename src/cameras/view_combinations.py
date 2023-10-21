# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

import utils
addon = utils.bpy.Addon()

def update(blcam, preferences):
    update_collection_combination(blcam, preferences)
    return None

def update_collection_combination(blcam, preferences):
    update_collection_combination_props(
        bpy.context.view_layer.layer_collection.children[preferences.container_props],
        [f"PR:{blcam.name}",],
    )

    update_collection_combination_blockouts(
        bpy.context.view_layer.layer_collection.children[preferences.container_cameras].children[preferences.container_blockouts],
        [f"BK:{blcam.name}",],
    )
    return None

def update_collection_combination_props(container, target):
    for bllaycol in container.children:
        if bllaycol.name in target:
            bllaycol.exclude = False
        else:
            bllaycol.exclude = True
    return None

def update_collection_combination_blockouts(container, target):
    for bllaycol in container.children:
        if bllaycol.name in target:
            bllaycol.exclude = False
        else:
            bllaycol.exclude = True

    for name in target:
        if utils.bpy.col.obt(name) is not None:
            for blob in utils.bpy.col.obt(name).objects:
                blob.visible_camera = False
                blob.visible_diffuse = False
                blob.visible_glossy = False
                blob.visible_transmission = False
                blob.visible_volume_scatter = False
    return None

class collection_hierarchy():
    @staticmethod
    def create(blcam, preferences):
        name = blcam.name

        blcol_blockouts = utils.bpy.col.obt(preferences.container_blockouts, force=True)
        utils.bpy.col.obt(f"BK:{name}", force=True, parent=blcol_blockouts)
        blcol_props = utils.bpy.col.obt(preferences.container_props, force=True)
        utils.bpy.col.obt(f"PR:{name}", force=True, parent=blcol_props)
        return None

    @staticmethod
    def update(blcam, preferences):
        name = blcam.name
        pr_cam = getattr(blcam.data, addon.name)

        blcol_blockouts = utils.bpy.col.obt(preferences.container_blockouts, force=True)
        cam_blockouts = utils.bpy.col.obt(pr_cam.hierarchy.blockouts, parent=blcol_blockouts)
        blcol_props = utils.bpy.col.obt(preferences.container_props, force=True)
        cam_props = utils.bpy.col.obt(pr_cam.hierarchy.props, parent=blcol_props)

        cam_blockouts.name = f"BK:{name}"
        cam_props.name = f"PR:{name}"
        return None

    @staticmethod
    def remove(blcam, preferences):
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
    def audit(blcam, preferences):
        name = blcam.name

        conditions = [
            utils.bpy.col.obt(preferences.container_blockouts),
            utils.bpy.col.obt(f"BK:{name}", local=True),
            utils.bpy.col.obt(preferences.container_props),
            utils.bpy.col.obt(f"PR:{name}", local=True),
        ]
        return all(conditions)

    @staticmethod
    def audit_previous(blcam, preferences):
        props = getattr(blcam.data, addon.name)

        conditions = [
            utils.bpy.col.obt(preferences.container_blockouts),
            utils.bpy.col.obt(props.hierarchy.blockouts, local=True),
            utils.bpy.col.obt(preferences.container_props),
            utils.bpy.col.obt(props.hierarchy.props, local=True),
        ]
        return all(conditions)

    @staticmethod
    def save_refs(blcam):
        props = getattr(blcam.data, addon.name)
        name = blcam.name
        props.hierarchy.blockouts = f"BK:{name}"
        props.hierarchy.props = f"PR:{name}"
        return None

    @staticmethod
    def cleanse_refs(blcam):
        props = getattr(blcam.data, addon.name)
        props.hierarchy.blockouts = ""
        props.hierarchy.props = ""
        return None

@addon.property
class WindowManager_Cameras_ViewCombinations(bpy.types.PropertyGroup):
    pass

@addon.property
class Preferences_Cameras_ViewCombinations(bpy.types.PropertyGroup):
    pass

CLASSES = [
    WindowManager_Cameras_ViewCombinations,
    Preferences_Cameras_ViewCombinations,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
