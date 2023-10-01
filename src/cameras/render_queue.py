# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

import utils
addon = utils.bpy.Addon()

@addon.property
class WindowManager_Cameras_RenderQueue(bpy.types.PropertyGroup):
    pass

@addon.property
class Preferences_Cameras_RenderQueue(bpy.types.PropertyGroup):
    pass

CLASSES = [
    Scene_Cameras_RenderQueue,
    WindowManager_Cameras_RenderQueue,
    Preferences_Cameras_RenderQueue,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
