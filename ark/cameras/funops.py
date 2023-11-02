# SPDX-License-Identifier: GPL-2.0-or-later
import math

import bpy
from ark import utils
addon = utils.bpy.Addon()

from . import properties
from . import view_combinations

def add_camera_hierarchy(blcam, preferences, renamed=False):
    if renamed:
        view_combinations.collection_hierarchy.update(blcam, preferences)
        view_combinations.update(blcam, preferences)
    else:
        view_combinations.collection_hierarchy.create(blcam, preferences)
    view_combinations.collection_hierarchy.save_refs(blcam)
    return None

def set_camera_active(blcam, preferences):
    bpy.context.scene.camera = blcam

    blcol_cameras = utils.bpy.col.obt(preferences.container_cameras, local=True)

    obt_camera_tracker(preferences.trackers_camera, blcam, blcol_cameras)
    update_camera_properties(blcam, preferences)
    return None

def obt_camera_tracker(tracker_name, blcam, blcol):
    tracker = utils.bpy.obj.obt(tracker_name, parent=blcol, force=True, local=True)
    tracker.matrix_world = blcam.matrix_world

    tracker.hide_select = True
    tracker.hide_select = True
    tracker.hide_viewport = True
    return None

def update_camera_properties(blcam, preferences):
    context = bpy.context
    pr_cam = getattr(blcam.data, addon.name)
    properties.Camera.update_exposure(pr_cam, context)
    properties.Camera.update_resolution(pr_cam, context)
    view_combinations.update(blcam, preferences)
    return None

def add_camera(preferences):
    name = preferences.default_name
    blcol_cameras = utils.bpy.col.obt(preferences.container_cameras)

    bldata = utils.bpy.obt(
        bpy.data.cameras,
        name,
        force=True,
        overwrite='NEW',
    )

    blcam =  utils.bpy.obj.obt(
        name,
        data=bldata,
        force=True,
        parent=blcol_cameras,
        overwrite='NEW',
    )

    force_camera_verticals(blcam)
    add_camera_hierarchy(blcam, preferences)
    set_camera_active(blcam, preferences)
    return None

def duplicate_camera(blcam, preferences):
    name = preferences.default_name
    blcol_cameras = utils.bpy.col.obt(preferences.container_cameras)

    new_cam = blcam.copy()
    new_cam.data = blcam.data.copy()
    view_combinations.collection_hierarchy.cleanse_refs(new_cam)

    blcol_cameras.objects.link(new_cam)

    set_camera_active(new_cam, preferences)
    add_camera_hierarchy(new_cam, preferences)
    return None

def remove_camera(blcam, preferences):
    if view_combinations.collection_hierarchy.audit(blcam, preferences):
        view_combinations.collection_hierarchy.remove(blcam, preferences)

    utils.bpy.obj.remove(blcam, purge_data=True)
    return None

def force_camera_verticals(blcam):
    _rotation_mode = blcam.rotation_mode
    blcam.rotation_mode = 'XYZ'
    blcam.rotation_euler[0] = math.radians(90)
    blcam.rotation_euler[1] = math.radians(0)
    blcam.rotation_mode = _rotation_mode
    return None

def audit_camera_verticals(blcam):
    conditions = [
        math.isclose(blcam.rotation_euler[0], math.radians(90), rel_tol=0.1),
        math.isclose(blcam.rotation_euler[1], math.radians(0), rel_tol=0.1),
    ]
    return all(conditions)

def get_camera_list(container, mode=None):
    if container is None:
        return None
    mode = 'ALL' if mode is None else mode
    match mode:
        case 'ACTIVE':
            return [bpy.context.scene.camera]
        case 'ALL':
            return [obj for obj in container.all_objects if obj.type == 'CAMERA']
        case 'MARKED':
            return [obj for obj in container.all_objects if obj.type == 'CAMERA' and utils.rgetattr(obj.data, f"{addon.name}.render")]
        case 'SELECTED':
            return [obj for obj in container.all_objects if obj.type == 'CAMERA' and obj.select_get()]
        case _:
            return []
