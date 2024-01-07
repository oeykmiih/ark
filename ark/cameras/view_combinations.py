# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from ark import utils
addon = utils.bpy.Addon()

def add(bl_cam, context, preferences):
    pr_cam = getattr(bl_cam.data, addon.name)
    pr_cam.view.world = context.scene.world
    structure.create(bl_cam, preferences)
    return None

def update(bl_cam, context, preferences):
    pr_cam = getattr(bl_cam.data, addon.name)
    context.scene.world = pr_cam.view.world

    update_collections(bl_cam, context, preferences)
    return None

def update_collections(bl_cam, context, preferences):
    pr_cam = getattr(bl_cam.data, addon.name)

    update_collection_props(
        context.view_layer.layer_collection.children[preferences.container_viewcombinations],
        [pr_cam.view.props.name],
    )
    return None

def update_collection_props(container, target):
    for bllaycol in container.children:
        if bllaycol.name in target:
            bllaycol.exclude = False
        else:
            bllaycol.exclude = True
    return None

def cleanse(bl_cam):
    pr_cam = getattr(bl_cam.data, addon.name)
    pr_cam.view.props = None
    pr_cam.view.world = None
    return None

class structure():
    @staticmethod
    def create(bl_cam, preferences):
        pr_cam = getattr(bl_cam.data, addon.name)

        blcol_viewcombinations = utils.bpy.col.obt(preferences.container_viewcombinations, force=True)
        pr_cam.view.props = utils.bpy.col.obt(f"VC:{bl_cam.name}", force=True, parent=blcol_viewcombinations)
        return None

    @staticmethod
    def update(bl_cam, preferences):
        name = bl_cam.name
        pr_cam = getattr(bl_cam.data, addon.name)

        blcol_viewcombinations = utils.bpy.col.obt(preferences.container_viewcombinations, force=True)
        cam_props = pr_cam.view.props

        cam_props.name = f"VC:{name}"
        return None

    @staticmethod
    def remove(bl_cam, preferences):
        pr_cam = getattr(bl_cam.data, addon.name)

        blcol_viewcombinations = utils.bpy.col.obt(preferences.container_viewcombinations, force=True)
        cam_props = pr_cam.view.props

        utils.bpy.col.empty(cam_props, objects=True)
        blcol_viewcombinations.children.unlink(cam_props)
        return None

    @staticmethod
    def audit(bl_cam, preferences):
        pr_cam = getattr(bl_cam.data, addon.name)

        conditions = [
            utils.bpy.col.obt(preferences.container_viewcombinations),
            utils.bpy.col.obt(pr_cam.view.props.name, local=True),
        ]
        return all(conditions)

    @staticmethod
    def audit_previous(bl_cam, preferences):
        pr_cam = getattr(bl_cam.data, addon.name)

        conditions = [
            utils.bpy.col.obt(preferences.container_viewcombinations),
            utils.bpy.col.obt(pr_cam.view.props.name, local=True),
        ]
        return all(conditions)

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
