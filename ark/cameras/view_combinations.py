# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from ark import utils
addon = utils.bpy.Addon()

def update(blcam, preferences):
    update_collection_combination(blcam, preferences)
    return None

def update_collection_combination(blcam, preferences):
    update_collection_combination_props(
        bpy.context.view_layer.layer_collection.children[preferences.container_viewcombinations],
        [f"VC:{blcam.name}",],
    )
    return None

def update_collection_combination_props(container, target):
    for bllaycol in container.children:
        if bllaycol.name in target:
            bllaycol.exclude = False
        else:
            bllaycol.exclude = True
    return None

class collection_hierarchy():
    @staticmethod
    def create(blcam, preferences):
        name = blcam.name

        blcol_viewcombinations = utils.bpy.col.obt(preferences.container_viewcombinations, force=True)
        utils.bpy.col.obt(f"VC:{name}", force=True, parent=blcol_viewcombinations)
        return None

    @staticmethod
    def update(blcam, preferences):
        name = blcam.name
        pr_cam = getattr(blcam.data, addon.name)

        blcol_viewcombinations = utils.bpy.col.obt(preferences.container_viewcombinations, force=True)
        cam_props = utils.bpy.col.obt(pr_cam.hierarchy.props, parent=blcol_viewcombinations)

        cam_props.name = f"VC:{name}"
        return None

    @staticmethod
    def remove(blcam, preferences):
        name = blcam.name

        blcol_viewcombinations = utils.bpy.col.obt(preferences.container_viewcombinations, force=True)
        cam_props = utils.bpy.col.obt(f"VC:{name}", local=True)

        utils.bpy.col.empty(cam_props, objects=True)
        blcol_viewcombinations.children.unlink(cam_props)
        return None

    @staticmethod
    def audit(blcam, preferences):
        name = blcam.name

        conditions = [
            utils.bpy.col.obt(preferences.container_viewcombinations),
            utils.bpy.col.obt(f"VC:{name}", local=True),
        ]
        return all(conditions)

    @staticmethod
    def audit_previous(blcam, preferences):
        pr_cam = getattr(blcam.data, addon.name)

        conditions = [
            utils.bpy.col.obt(preferences.container_viewcombinations),
            utils.bpy.col.obt(pr_cam.hierarchy.props, local=True),
        ]
        return all(conditions)

    @staticmethod
    def save_refs(blcam):
        pr_cam = getattr(blcam.data, addon.name)
        name = blcam.name
        pr_cam.hierarchy.props = f"VC:{name}"
        return None

    @staticmethod
    def cleanse_refs(blcam):
        pr_cam = getattr(blcam.data, addon.name)
        pr_cam.hierarchy.props = ""
        return None

    @staticmethod
    def get_viewcombination(blcam):
        pr_cam = getattr(blcam.data, addon.name)
        return utils.bpy.col.obt(pr_cam.hierarchy.props, local=True)

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
