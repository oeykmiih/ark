# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import contextlib
import time
import io
import os

from ark import utils
addon = utils.bpy.Addon()

from . import funops
from . import enums

TOKENS = {
    "$foo" : "BAR",
}

def preview_path(context):
    tokens = {}
    tokens["$camera"] = context.scene.camera.name
    tokens["$date"] = time.strftime("%y%m%d")
    tokens["$time"] = time.strftime("%H%M%S")

    filepath = context.scene.render.filepath
    # NOTE: Make fileoutput blender folder if file output is empty
    dirpath = "//" if filepath == "" else filepath
    dirpath = replace_tokens(dirpath, tokens=tokens)
    # dirpath = bpy.path.abspath(dirpath)
    return bpy.path.native_pathsep(dirpath)

def replace_tokens(filepath, tokens):
    for token, value in tokens.items():
        if token in filepath:
            filepath = filepath.replace(token, value)
    return filepath

class ARK_OT_RenderQueue(bpy.types.Operator):
    bl_idname = f"{addon.name}.render_queue"
    bl_label = ""

    _timer = None
    _fpath = None
    stop = False
    rendering = False
    shots = None

    mode : bpy.props.EnumProperty(
        name = "",
        items = enums.RENDER_MODE,
        default = 'ACTIVE',
    )
    slots : bpy.props.BoolProperty()
    export : bpy.props.BoolProperty()

    def set_filepath(self, context, blcam):
        pr_cam = getattr(blcam.data, addon.name)

        # NOTE: Make fileoutput blender folder if file output is empty
        dirpath = "//" if self._fpath == "" else self._fpath
        # NOTE: Make fileoutput absolute to easier handling
        dirpath = bpy.path.abspath(dirpath)
        dirpath = replace_tokens(dirpath, TOKENS)

        if not os.path.isdir(dirpath):
            try:
                os.makedirs(dirpath)
            except:
                raise

        context.scene.render.filepath = dirpath
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
        context.scene.render.filepath = self._fpath
        bpy.context.window_manager.event_timer_remove(self._timer)
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
        self._fpath = context.scene.render.filepath

        if not context.blend_data.is_saved:
            self.report({'ERROR'}, "File needs to be saved before batch rendering")
            return {'CANCELLED'}

        if context.scene.render.is_movie_format:
            self.report({'ERROR'}, "Video output formats are not supported, please use Image ouput format")
            return {'CANCELLED'}

        blcol_cameras = utils.bpy.col.obt(self.preferences.container_cameras, local=True)
        self.shots = funops.get_camera_list(blcol_cameras, mode=self.mode)

        if not self.shots:
            self.report({'INFO'}, "No cameras to render")
            return {'CANCELLED'}

        if self.slots:
            self.bump_render_slot(context)

        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)
        self._timer = bpy.context.window_manager.event_timer_add(1, window=bpy.context.window)
        bpy.context.window_manager.modal_handler_add(self)
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
                funops.set_camera_active(self.shots[0], self.preferences)
                TOKENS["$camera"] = self.shots[0].name

                if self.export:
                    try:
                        self.set_filepath(context, self.shots[0])
                    except:
                        self.terminate(context)
                        self.report({'ERROR'}, "Invalid path, the render has been cancelled")
                        return {'CANCELLED'}

                bpy.ops.render.render('INVOKE_DEFAULT', write_still=self.export)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        TOKENS["$date"] = time.strftime("%y%m%d")
        TOKENS["$time"] = time.strftime("%H%M%S")
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
