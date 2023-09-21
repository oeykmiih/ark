import bpy
import bl_ui

import utils
addon = utils.bpy.Addon()

from . import enums

class ARK_OT_QuickAssetBrowser(bpy.types.Operator):
    bl_idname = f"{addon.name}.quick_asset_browser"
    bl_label = ""
    bl_options = {'INTERNAL'}

    def execute(self, context):
        preferences = addon.preferences
        session = addon.session

        split_direction = 'VERTICAL'
        split_factor = preferences.split_factor

        old = None
        # Check whether there is an asset browser open somewhere.
        for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.ui_type == 'ASSETS':
                        old = area

        if old is None:
            areas = []
            # Load all areas into list
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    areas.append(area)

            session.context = context.area.ui_type

            # Split current area
            bpy.ops.screen.area_split(direction=split_direction,factor=split_factor)

            # Look for area not in list and override context
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area not in areas:
                        with context.temp_override(area=area):
                            context.area.ui_type = 'ASSETS'
                            context.space_data.show_region_toolbar = False

                            bpy.app.timers.register(self.set_asset_browser_defaults, first_interval=.005)
                        break
        else:
            with context.temp_override(area=old):
                bpy.ops.screen.area_close()
        return {"INTERFACE"}

    @staticmethod
    def set_asset_browser_defaults():
        preferences = addon.preferences
        session = addon.session
        for area in bpy.context.screen.areas:
            if area.ui_type == 'ASSETS':
                with bpy.context.temp_override(area=area):
                    if session.library:
                        bpy.context.space_data.params.asset_library_ref = session.library
                    else:
                        bpy.context.space_data.params.asset_library_ref = preferences.library
                break
        return None

@addon.property
class ARK_WindowManager_Interface_QuickAssetBrowser(bpy.types.PropertyGroup):
    context : bpy.props.StringProperty(
        name="ARK_OT_ToogleAssetBrowser_context",
        default="",
    )

    library : bpy.props.StringProperty(
        name = "ARK_OT_ToogleAssetBrowser_library",
        default = "",
    )

@addon.property
class ARK_Preferences_Interface_QuickAssetBrowser(bpy.types.PropertyGroup):
    def get_libraries(self, context):
        # NOTE: Use Blender built-in libraries aswell.
        items = [
            ('ALL', "All", ""),
            ('LOCAL', "Local", ""),
            ('ESSENTIALS', "Essentials", ""),
        ]

        for lib in bpy.context.preferences.filepaths.asset_libraries.keys():
            items.append((lib, lib, ""))
        return items

    library : bpy.props.EnumProperty(
        name = "QuickAssetBrowser Library",
        items = get_libraries,
        default = None,
    )

    split_factor : bpy.props.FloatProperty(
        name = "ARK_OT_ToogleAssetBrowser_library",
        default = 0.3,
    )

def Preferences_UI(preferences, layout):
    layout.prop(preferences, "library")
    split = layout.row(align=True).split(factor=0.245)
    split.label(text="QuickAssetBrowser Factor")
    split.prop(preferences, "split_factor", text="")
    return None

CLASSES = [
    ARK_OT_QuickAssetBrowser,
    ARK_Preferences_Interface_QuickAssetBrowser,
    ARK_WindowManager_Interface_QuickAssetBrowser,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
