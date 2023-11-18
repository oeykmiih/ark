# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
addon = utils.bpy.Addon()

MODULES = {
    "hdri" : None,
    "properties" : None,
}
MODULES = utils.import_modules(MODULES)

class ARK_PT_PROPERTIES_World(bpy.types.Panel):
    bl_label = "World"
    bl_idname = "ARK_PT_PROPERTIES_World"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        preferences = addon.preferences
        session = addon.session
        world = context.scene.world

        if world is not None:
            pr_world = getattr(world, addon.name)

            col = layout.column(align=True)
            header = col.box().row()
            info = header.row(align=True)
            buttons = header.row(align=True)
            buttons.alignment = 'RIGHT'
            body = col.box()

            if pr_world.created:
                info.prop(pr_world, "kind", expand=True)

                match pr_world.kind:
                    case 'HDRI':
                        if not hdri.audit_library():
                            buttons.label(text="")
                            utils.bpy.ui.alert(body, text="Missing HDRI Library")
                            row = utils.bpy.ui.split(body, text="HDRI Library")
                            row.prop(addon.preferences.hdri, "library", text="")
                        else:
                            buttons.operator(hdri.ARK_OT_ReloadHDRIPreviews.bl_idname, icon='FILE_REFRESH')
                            body.template_icon_view(session.hdri, "previews", scale=10)
                    case 'SKY':
                        buttons.label(text="")
                        body.label(text="SKY is selected.")
            else:
                utils.bpy.ui.alert(info, text="Missing ARK World")
                buttons.label(text="")
                body.scale_y = 1.5
                body.operator(hdri.ARK_OT_CreateWorldHDRI.bl_idname, text="Add HDRI")
        return None

@addon.property
class WindowManager_Worlds(bpy.types.PropertyGroup):
    pass

@addon.property
class Preferences_Worlds(bpy.types.PropertyGroup):
    pass

def UI(preferences, layout):
    for name in (name for name, module in MODULES.items() if hasattr(module, "UI")):
        module = MODULES[name]
        box = layout.box()
        box.label(text=name.replace("_", " ").title())
        properties = getattr(preferences, name)
        module.UI(properties, box)
    return None

CLASSES = [
    ARK_PT_PROPERTIES_World,
    WindowManager_Worlds,
    Preferences_Worlds,
]

def register():
    utils.bpy.register_modules(MODULES)
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    utils.bpy.unregister_modules(MODULES)
    return None
