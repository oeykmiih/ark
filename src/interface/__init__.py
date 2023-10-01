# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import contextlib
import io

import utils
addon = utils.bpy.Addon()

MODULES = {
    "headers" : None,
    "hide" : None,
    "quick_asset_browser" : None,
    "quick_editor" : None,
}
MODULES = utils.import_modules(MODULES)

class ARK_OT_ToggleInterface(bpy.types.Operator):
    bl_idname = f"{addon.name}.toggle_interface"
    bl_label = ""
    bl_options = {'INTERNAL'}

    # NOTE: This disables the Operator for everything but the TOPBAR.
    ## Only needed because the operator appears when searching since it's
    ## present in a menu (TOPBAR_MT_editor_menus).
    @classmethod
    def poll(self, context):
        return context.area.ui_type == ''

    @staticmethod
    def run():
        preferences = addon.preferences
        session = addon.session

        for name in MODULES.keys():
            sub = getattr(session, name)
            if hasattr(sub, "toggle"):
                sub.toggle = not session.toggle

        session.toggle = not session.toggle

        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return None

    def execute(self, context):
        self.run()
        return {'INTERFACE'}
    pass

def ARK_BT_UPPERBAR_ToggleInterface(self, context):
    session = addon.session

    row = self.layout.row(align=True)
    row.ui_units_x = 3
    op = row.operator(
        ARK_OT_ToggleInterface.bl_idname,
        text="Simplify!",
        emboss = session.toggle,
        depress = session.toggle,
    )
    return None

@addon.property
class WindowManager_Interface(bpy.types.PropertyGroup):
    toggle : bpy.props.BoolProperty(
        name = "Simplfiy",
        default = False,
    )

@addon.property
class Preferences_Interface(bpy.types.PropertyGroup):
    enable_on_startup : bpy.props.BoolProperty(
        name = "Enable on startup!",
        default = False,
    )

def UI(preferences, layout):
    box = layout.box()
    box.prop(preferences, "enable_on_startup", toggle=True)

    items = (name for name, module in MODULES.items() if hasattr(module, "UI"))
    for name in items:
        module = MODULES[name]
        box = layout.box()
        box.label(text=name.replace("_", " ").title())
        properties = getattr(preferences, name)
        module.UI(properties, box)
    return None

CLASSES = [
    ARK_OT_ToggleInterface,
    WindowManager_Interface,
    Preferences_Interface,
]

@bpy.app.handlers.persistent
def load_post(self):
    preferences = addon.preferences
    session = addon.session
    if not preferences.enable_on_startup:
        session.toggle = True
    ARK_OT_ToggleInterface.run()
    return None

@bpy.app.handlers.persistent
def load_pre(self):
    session = addon.session

    session.toggle = False
    return None

    # NOTE: bpy.app.load_pre handler doesn't seem to work with app templates,
    ## so we can't disable before and enable after loading a file, will raise Exception.

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)

    bpy.types.TOPBAR_MT_editor_menus.append(ARK_BT_UPPERBAR_ToggleInterface)
    bpy.app.handlers.load_post.append(load_post)
    bpy.app.handlers.load_pre.append(load_pre)
    return None

def unregister():
    bpy.app.handlers.load_pre.remove(load_pre)
    bpy.app.handlers.load_post.remove(load_post)
    bpy.types.TOPBAR_MT_editor_menus.remove(ARK_BT_UPPERBAR_ToggleInterface)

    utils.bpy.unregister_classes(CLASSES)
    utils.bpy.unregister_modules(MODULES)
    return None
