# SPDX-License-Identifier: GPL-2.0-or-later
import json
import os

import bpy
from ark import utils
addon = utils.bpy.Addon()

class ARK_OT_CopyPreferences(bpy.types.Operator):
    """Copies all (possible) preferences"""
    bl_idname = "ark.copy_preferences"
    bl_label = "Copy Preferences"

    def execute(self, context):
        rna_paths = [
            "bpy.context.preferences.filepaths",
            "bpy.context.preferences.view",
            "bpy.context.preferences.system",
        ]
        bpy.context.window_manager.clipboard = utils.bpy.rna2json.dump_multiple(rna_paths)
        return {'FINISHED'}

class ARK_OT_VIEW3D_CopyViewportSettings(bpy.types.Operator):
    """Copies viewport settings to clipboard."""
    bl_idname = "ark.copy_viewport_settings"
    bl_label = "Copy View3D Settings"

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == "VIEW_3D"

    def execute(self, context):
        rna_paths = [
            "bpy.context.space_data.shading",
            "bpy.context.space_data.overlay",
        ]
        bpy.context.window_manager.clipboard = utils.bpy.rna2json.dump_multiple(rna_paths)
        return {'FINISHED'}

    @staticmethod
    def button(self, context):
        self.layout.operator(__class__.bl_idname, text=__class__.bl_label)
        return None

class ARK_OT_ApplyJSONProperties(bpy.types.Operator):
    """Applies settings from clipboard."""
    bl_idname = "ark.apply_json_properties"
    bl_label = "Apply JSON"

    @classmethod
    def poll(cls, context):
        return bpy.context.window_manager.clipboard is not None

    def execute(self, context):
        utils.bpy.rna2json.load(bpy.context.window_manager.clipboard)
        return {'FINISHED'}

    @staticmethod
    def button(self, context):
        self.layout.operator(__class__.bl_idname, text=__class__.bl_label)
        return None

@addon.property
class WindowManager_Interface_Presets(bpy.types.PropertyGroup):
    pass

@addon.property
class Preferences_Interface_Presets(bpy.types.PropertyGroup):
    pass

CLASSES = [
    ARK_OT_VIEW3D_CopyViewportSettings,
    ARK_OT_CopyPreferences,
    ARK_OT_ApplyJSONProperties,
    WindowManager_Interface_Presets,
    Preferences_Interface_Presets,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None