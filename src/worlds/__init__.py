# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import utils
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

            box = layout.box()
            col = box.column(align=True)
            match pr_world.kind:
                case 'NONE':
                    col.scale_y = 1.5
                    col.operator(hdri.ARK_OT_CreateWorldHDRI.bl_idname, text="Add HDRI")
                case 'HDRI':
                    row = col.row()
                    if hdri.audit_library():
                        row.template_icon_view(session.hdri, "previews", scale=10)
                        side = row.column()
                        side.operator(hdri.ARK_OT_ReloadHDRIPreviews.bl_idname, icon='FILE_REFRESH')
                    else:
                        row.prop(addon.preferences.hdri, "library", text="")
                case 'SKY':
                    col.label(text="SKY is selected.")
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
