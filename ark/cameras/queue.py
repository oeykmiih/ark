# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import contextlib
import time
import io
import os

from ark import utils
addon = utils.bpy.Addon()

from . import common
from . import enums

TOKENS = {
    "$foo" : "BAR",
}

def preview_path(context):
    pr_queue = addon.get_property("scene")
    tokens = {}
    tokens["$file"] = bpy.path.display_name_from_filepath(bpy.data.filepath)
    tokens["$camera"] = context.scene.camera.name
    tokens["$date"] = time.strftime("%y%m%d")
    tokens["$time"] = time.strftime("%H%M%S")

    path_folder = replace_tokens(pr_queue.path_folder, tokens=tokens)
    path_folder = "//" if path_folder == "" else path_folder

    path_file = replace_tokens(pr_queue.path_file, tokens=tokens)

    path_full = os.path.join(path_folder, path_file)
    return bpy.path.native_pathsep(path_full)

def replace_tokens(filepath, tokens):
    for token, value in tokens.items():
        if token in filepath:
            filepath = filepath.replace(token, value)
    return filepath

class ARK_OT_RenderQueue(bpy.types.Operator):
    bl_idname = f"{addon.name}.queue"
    bl_label = ""

    _timer = None
    stop = False
    rendering = False
    shots = None

    slots : bpy.props.BoolProperty()
    export : bpy.props.BoolProperty()
    mode : bpy.props.EnumProperty(
        name = "",
        items = enums.RENDER_MODE,
        default = 'ACTIVE',
    )

    def set_filepath(self, context):
        pr_queue = addon.get_property("scene")

        path_folder = replace_tokens(pr_queue.path_folder, tokens=TOKENS)
        path_folder = "//" if path_folder == "" else path_folder

        path_file = replace_tokens(pr_queue.path_file, tokens=TOKENS)

        path_folder = bpy.path.abspath(path_folder)
        path_full = os.path.join(path_folder, path_file)

        if not os.path.isdir(path_folder):
            os.makedirs(path_folder)

        context.scene.render.filepath = path_full
        return None

    @staticmethod
    def bump_render_slot(context):
        if "Render Result" in bpy.data.images:
            render_result = bpy.data.images["Render Result"]
            if render_result.has_data:
                slot = render_result.render_slots.active_index
                slot += 1
                slot %= 8
                render_result.render_slots.active_index = slot
        return None

    def pre(self, context, thrd = None):
        self.rendering = True
        return None

    def post(self, context, thrd = None):
        self.shots.pop(0)
        self.rendering = False
        if self.slots and self.shots:
            self.bump_render_slot(context)
        return None

    def cancelled(self, context, thrd = None):
        self.stop = True
        self.report({'INFO'}, "Cancelled by user")
        return None

    def terminate(self, context):
        context.scene.render.filepath = self.path_folder
        context.window_manager.event_timer_remove(self._timer)
        bpy.app.handlers.render_cancel.remove(self.cancelled)
        bpy.app.handlers.render_post.remove(self.post)
        bpy.app.handlers.render_pre.remove(self.pre)
        # NOTE: Redraw at the end to have the shown active camera match
        ## the rendered camera instead of last one.
        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {}

    def execute(self, context):
        self.preferences = addon.parent_preferences
        self.path_folder = context.scene.render.filepath

        if not context.blend_data.is_saved:
            self.report({'ERROR'}, "File needs to be saved before batch rendering")
            return {'CANCELLED'}

        if context.scene.render.is_movie_format:
            self.report({'ERROR'}, "Video output formats are not supported, please use Image ouput format")
            return {'CANCELLED'}

        blcol_cameras = utils.bpy.col.obt(self.preferences.container_cameras, local=True)
        self.shots = common.get_camera_list(blcol_cameras, context, mode=self.mode)

        if not self.shots:
            self.report({'INFO'}, "No cameras to render")
            return {'CANCELLED'}

        if self.slots:
            self.bump_render_slot(context)

        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)
        self._timer = context.window_manager.event_timer_add(1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            self.terminate(context)
            self.report({'INFO'}, "Cancelled by user")
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if not self.shots or self.stop:
                self.terminate(context)
                self.report({'INFO'}, "Finished rendering")
                return {'FINISHED'}

            if not self.rendering:
                common.set_camera_active(self.shots[0], context, self.preferences)
                TOKENS["$camera"] = self.shots[0].name

                if self.export:
                    try:
                        self.set_filepath(context)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        self.terminate(context)
                        self.report({'ERROR'}, "Invalid path, the render has been cancelled")
                        return {'CANCELLED'}

                bpy.ops.render.render('INVOKE_DEFAULT', write_still=self.export)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        TOKENS["$date"] = time.strftime("%y%m%d")
        TOKENS["$time"] = time.strftime("%H%M%S")
        TOKENS["$file"] = bpy.path.display_name_from_filepath(bpy.data.filepath)
        return self.execute(context)

@addon.property
class Scene_Cameras_RenderQueue(bpy.types.PropertyGroup):
    mode : bpy.props.EnumProperty(
        name = "Render Mode",
        items = enums.RENDER_MODE,
        default = 'ACTIVE',
    )

    slots : bpy.props.BoolProperty(
        name = "Use Render Slots",
        description = "Use render slots",
        default = True,
    )

    export : bpy.props.BoolProperty(
        name = "Export Renders",
        description = "Save finished renders to specificed path",
        default = True,
    )

    path_folder : bpy.props.StringProperty(
        name = "Folder",
        default = "//",
        subtype = 'FILE_PATH',
    )

    path_file : bpy.props.StringProperty(
        name = "File",
        default = "$camera",
    )

@addon.property
class WindowManager_Cameras_RenderQueue(bpy.types.PropertyGroup):
    pass

@addon.property
class Preferences_Cameras_RenderQueue(bpy.types.PropertyGroup):
    pass

CLASSES = [
    ARK_OT_RenderQueue,
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
