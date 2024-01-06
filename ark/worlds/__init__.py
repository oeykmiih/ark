# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from ark import utils
addon = utils.bpy.Addon()

MODULES = {
    "common" : None,
    "enums" : None,
    "hdri" : None,
    "sun_position" : None,
    "sky" : None,
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

        col = layout.column(align=True)
        header = col.box().row()
        info = header.row(align=True)
        buttons = header.row(align=True)
        buttons.alignment = 'LEFT'
        body = col.box()

        if world is None:
            utils.bpy.ui.label(info, text=f"No active world")
            utils.bpy.ui.empty(buttons, emboss=False)
            buttons.scale_x = 1.0

            body.row(align=True).prop(session, "kind", expand=True)
            _ = body.row(align=True)
            _.template_ID(context.scene, "world", new=ARK_OT_CreateWorld.bl_idname)
            # _.operator(ARK_OT_CreateWorld.bl_idname, text="New", icon='ADD')
        else:
            pr_world = getattr(world, addon.name)
            body.row(align=True).prop(pr_world, "kind", expand=True)
            match pr_world.kind:
                case 'HDRI':
                    if not hdri.audit_library():
                        utils.bpy.ui.label(info, text="Missing HDRI Library.")
                        utils.bpy.ui.empty(buttons, emboss=False)
                        buttons.scale_x = 1.0

                        row = utils.bpy.ui.split(body.row(align=True), text="HDRI Library")
                        row.prop(preferences.hdri, "library", text="")
                    #TODO: create function to check if world is hdri and all nodes are there
                    else:
                        if not hdri.audit_world(world):
                            info.alert = True
                            info.operator(hdri.ARK_OT_CreateWorldHDRI.bl_idname, text="Missing world nodes, fix it?")
                            utils.bpy.ui.empty(buttons, emboss=False)
                            buttons.scale_x = 1.0
                        else:
                            _ = buttons.row()
                            _.alert=True
                            _.operator(ARK_OT_RemoveWorld.bl_idname, icon='X')

                            hdri.handle_existing_world(world)
                            body.template_icon_view(session.hdri, "preview", scale=10)

                            footer = col.box().row()
                            footer.alignment = 'RIGHT'
                            footer.operator(hdri.ARK_OT_ReloadHDRIPreviews.bl_idname, icon='NODE_COMPOSITING')

                            section = layout.box()
                            section.use_property_split = True
                            section.use_property_decorate = False

                            col = section.column(align=True)
                            row = utils.bpy.ui.split(col, text="Strength")
                            n_background = common.get_background_node(world)
                            if n_background is None:
                                row.enabled = False
                                utils.bpy.ui.label(row, text="")
                                utils.bpy.ui.alert(info, text="Missing background node.")
                            else:
                                row.prop(common.get_world_strength(world), "default_value", icon_only=True)

                                minus = row.operator(common.ARK_OT_SubLightStop.bl_idname, icon='REMOVE')
                                minus.mode = 'WORLD'
                                minus.world = world.name

                                plus = row.operator(common.ARK_OT_AddLightStop.bl_idname, icon='ADD')
                                plus.mode = 'WORLD'
                                plus.world = world.name

                            col = section.column(align=True)
                            col.use_property_split = False
                            row = utils.bpy.ui.split(col, text="Ray Visibility")
                            row.prop(world.cycles_visibility, "diffuse", toggle=True)
                            row.prop(world.cycles_visibility, "glossy", toggle=True)
                            row.prop(world.cycles_visibility, "camera", toggle=True)
                            row = utils.bpy.ui.split(col, text="Film Transparency")
                            row.prop(context.scene.render, "film_transparent", toggle=True)
                case 'SKY':
                    if not sky.audit_world(world):
                        info.alert = True
                        info.operator(sky.ARK_OT_CreateWorldSky.bl_idname, text="Missing world nodes, fix it?")
                        utils.bpy.ui.empty(buttons, emboss=False)
                        buttons.scale_x = 1.0
                    else:
                        _ = buttons.row()
                        _.alert=True
                        _.operator(ARK_OT_RemoveWorld.bl_idname, icon='X')

                        pr_sun = pr_world.sun_position

                        footer = col.box().row()
                        footer.alignment = 'RIGHT'
                        row = footer.row(align=True)
                        row.prop(preferences.sun_position, "show_overlays", icon='OVERLAY', icon_only=True)
                        sub = row.row(align=True)
                        sub.enabled = preferences.sun_position.show_overlays
                        sub.prop(pr_sun, "show_north", icon='PMARKER_SEL', icon_only=True)
                        sub.prop(pr_sun, "show_analemmas", icon='SHADING_WIRE', icon_only=True)
                        sub.prop(pr_sun, "show_surface", icon='SHADING_RENDERED', icon_only=True)

                        section = layout.box()
                        section.use_property_split = True
                        section.use_property_decorate = False

                        row = utils.bpy.ui.split(section, text="Strength")
                        n_background = common.get_background_node(world)
                        if n_background is None:
                            row.enabled = False
                            utils.bpy.ui.label(row, text="")
                            utils.bpy.ui.alert(info, text="Missing background node.")
                        else:
                            row.prop(common.get_world_strength(world), "default_value", icon_only=True)

                            minus = row.operator(common.ARK_OT_SubLightStop.bl_idname, icon='REMOVE')
                            minus.mode = 'WORLD'
                            minus.world = world.name

                            plus = row.operator(common.ARK_OT_AddLightStop.bl_idname, icon='ADD')
                            plus.mode = 'WORLD'
                            plus.world = world.name

                        col = section.column(align=True)
                        col.use_property_split = False
                        row = utils.bpy.ui.split(col, text="Ray Visibility")
                        row.prop(world.cycles_visibility, "diffuse", toggle=True)
                        row.prop(world.cycles_visibility, "glossy", toggle=True)
                        row.prop(world.cycles_visibility, "camera", toggle=True)
                        row = utils.bpy.ui.split(col, text="Film Transparency")
                        row.prop(context.scene.render, "film_transparent", toggle=True)

                        section = layout.box()
                        section.use_property_split = True
                        section.use_property_decorate = False

                        col = section.column(align=True)
                        col.prop(pr_sun, "north_offset")
                        col.prop(pr_sun, "coordinates")

                        row = utils.bpy.ui.split(col, text="Latitude/Longitude  ")
                        row.prop(pr_sun, "latitude", text="")
                        row.prop(pr_sun, "longitude", text="")

                        row = utils.bpy.ui.split(col, text="Day/Month/Year")
                        row.prop(pr_sun, "day", text="")
                        row.prop(pr_sun, "month", text="")
                        row.prop(pr_sun, "year", text="")

                        row = utils.bpy.ui.split(col, text="Azimuth", enabled=False)
                        row.prop(pr_sun, "sun_azimuth", text="")

                        row = utils.bpy.ui.split(col, text="Elevation", enabled=False)
                        row.prop(pr_sun, "sun_elevation", text="")

                        col = section.column(align=True)
                        col.prop_search(pr_sun, "sky_texture", world.node_tree, "nodes")
                        col.prop(pr_sun, "sun_object")

                        n_env = sky.get_env_node(world)
                        section = layout.box()
                        section.use_property_split = True
                        section.use_property_decorate = False

                        col = section.column(align=True)
                        col.prop(n_env, "sun_size")
                        col.prop(n_env, "sun_intensity")

                        col = section.column(align=True)
                        col.prop(n_env, "altitude")
                        col.prop(n_env, "air_density")
                        col.prop(n_env, "dust_density")
                        col.prop(n_env, "ozone_density")
                        # col.
        return None

class ARK_OT_CreateWorld(bpy.types.Operator):
    bl_idname = f"{addon.name}.create_world"
    bl_label = ""

    def execute(self, context):
        session = addon.session

        world = bpy.data.worlds.new("World")
        world.use_nodes = True
        world.node_tree.nodes.clear()
        context.scene.world = world

        match session.kind:
            case 'HDRI':
                hdri.create_world(world, context)
            case 'SKY':
                sky.create_world(world, context)
        return {'FINISHED'}

class ARK_OT_RemoveWorld(bpy.types.Operator):
    bl_idname = f"{addon.name}.remove_world"
    bl_label = ""

    def execute(self, context):
        context.scene.world = None
        return {'FINISHED'}

@addon.property
class WindowManager_Worlds(bpy.types.PropertyGroup):
    kind : bpy.props.EnumProperty(
        name = "kind",
        description = "kind",
        items = enums.WORLD_KIND,
        default = enums.WORLD_KIND[1][0],
    )

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
    ARK_OT_CreateWorld,
    ARK_OT_RemoveWorld,
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
