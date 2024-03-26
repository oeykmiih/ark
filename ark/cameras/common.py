# SPDX-License-Identifier: GPL-2.0-or-later
import math

import bpy
from ark import utils
addon = utils.bpy.Addon()

from . import properties
from . import views

def set_camera_active(bl_cam, context, preferences):
    context.scene.camera = bl_cam
    bl_cam.select_set(True)
    context.view_layer.objects.active = bl_cam

    blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, local=True)

    obt_camera_tracker(preferences.trackers_camera, bl_cam, blcol_cameras)
    update_camera_properties(bl_cam, context, preferences)
    return None

def get_next_camera(container):
    if container is None:
        return None
    bl_cam = None
    for obj in container.all_objects:
        if obj.type == 'CAMERA':
            bl_cam = obj
    return bl_cam

def set_next_camera_active(context, preferences):
    next_cam = get_next_camera(utils.bpy.col.obt(preferences.container_cameras))
    if next_cam:
        set_camera_active(next_cam, context, preferences)
    return None

def obt_camera_tracker(tracker_name, bl_cam, blcol):
    tracker = utils.bpy.obj.obt(tracker_name, parent=blcol, force=True, local=True)
    tracker.matrix_world = bl_cam.matrix_world

    tracker.hide_select = True
    tracker.hide_select = True
    tracker.hide_viewport = True
    return None

def update_camera_properties(bl_cam, context, preferences):
    pr_cam = getattr(bl_cam.data, addon.name)
    properties.Camera.update_exposure(pr_cam, context)
    properties.Camera.update_resolution(pr_cam, context)
    views.update(bl_cam, context, preferences)
    return None

def add_camera(context, preferences):
    name = preferences.default_name
    blcol_cameras = utils.bpy.col.obt(preferences.container_cameras)

    bldata = utils.bpy.obt(
        bpy.data.cameras,
        name,
        force=True,
        overwrite='NEW',
    )

    bl_cam = utils.bpy.obj.obt(
        name,
        data=bldata,
        force=True,
        parent=blcol_cameras,
        overwrite='NEW',
    )

    force_camera_verticals(bl_cam)
    views.add(bl_cam, context, preferences)

    bpy.ops.object.select_all(action='DESELECT')
    set_camera_active(bl_cam, context, preferences)
    return None

def _duplicate_camera(bl_cam, context, preferences):
    """Shared by duplicate_camera and duplicate_cameras"""
    name = preferences.default_name
    blcol_cameras = utils.bpy.col.obt(preferences.container_cameras)

    new_cam = bl_cam.copy()
    new_cam.data = bl_cam.data.copy()
    views.cleanse(new_cam)

    blcol_cameras.objects.link(new_cam)

    views.add(new_cam, context, preferences)
    new_cam.select_set(True)
    return new_cam

def duplicate_camera(bl_cam, context, preferences):
    """Duplicates a single camera"""
    bpy.ops.object.select_all(action='DESELECT')

    new_cam = _duplicate_camera(bl_cam, context, preferences)
    set_camera_active(new_cam, context, preferences)
    return None

def duplicate_cameras(bl_cams, context, preferences):
    """Duplicates multiple cameras"""
    bpy.ops.object.select_all(action='DESELECT')

    for bl_cam in bl_cams:
        new_cam = _duplicate_camera(bl_cam, context, preferences)
    set_camera_active(new_cam, context, preferences)
    return None

def remove_camera(bl_cam, context, preferences):
    if views.structure.audit(bl_cam, preferences):
        views.structure.remove(bl_cam, preferences)

    utils.bpy.obj.remove(bl_cam, purge_data=True)
    return None

def remove_cameras(bl_cams, context, preferences):
    for bl_cam in bl_cams:
        remove_camera(bl_cam, context, preferences)
    return None

def force_camera_verticals(bl_cam):
    _rotation_mode = bl_cam.rotation_mode
    bl_cam.rotation_mode = 'XYZ'
    bl_cam.rotation_euler[0] = math.radians(90)
    bl_cam.rotation_euler[1] = math.radians(0)
    bl_cam.rotation_mode = _rotation_mode
    return None

def audit_camera_verticals(bl_cam):
    conditions = [
        math.isclose(bl_cam.rotation_euler[0], math.radians(90), rel_tol=0.1),
        math.isclose(bl_cam.rotation_euler[1], math.radians(0), rel_tol=0.1),
    ]
    return all(conditions)

def get_camera_list(container, context, mode=None):
    if container is None:
        return None
    mode = 'ALL' if mode is None else mode
    match mode:
        case 'ACTIVE':
            return [context.scene.camera]
        case 'ALL':
            return [obj for obj in container.all_objects if obj.type == 'CAMERA']
        case 'MARKED':
            return [obj for obj in container.all_objects if obj.type == 'CAMERA' and utils.rgetattr(obj.data, f"{addon.name}.render")]
        case 'SELECTED':
            return [obj for obj in container.all_objects if obj.type == 'CAMERA' and obj.select_get()]
        case _:
            return []

def set_camera_list(collection_prop, container):
    collection_prop.clear()
    for obj in container.all_objects:
                if obj.type == 'CAMERA':
                    _ = collection_prop.add()
                    _.object = obj
    return
