# SPDX-License-Identifier: GPL-2.0-or-later
import io
import contextlib

import bpy

from ark import utils
addon = utils.bpy.Addon()

def find_materials_in_file(session):
    materials = bpy.data.materials
    if session.show_hidden:
        if session.show_orphan:
            return [blmat for blmat in materials if not blmat.is_grease_pencil]
        else:
            return [blmat for blmat in materials if not blmat.is_grease_pencil and blmat.users > 0]
    else:
        if session.show_orphan:
            return [blmat for blmat in materials if not blmat.is_grease_pencil and not blmat.name.startswith(".")]
        else:
            return [blmat for blmat in materials if not blmat.is_grease_pencil and not blmat.name.startswith(".") and blmat.users > 0]

def find_materials_in_instance(blcol):
    materials = []
    for blob in bpy.data.collections[blcol.instance_collection.name].objects:
        materials += find_materials_in_blob(blob)
    return materials

def find_materials_in_blob(blob):
    materials = []
    match blob.type:
        case 'EMPTY':
            if blob.instance_type == 'COLLECTION' and blob.instance_collection is not None:
                materials += find_materials_in_instance(blob)
        case 'MESH':
            materials += blob.data.materials
        case _:
            pass
    return materials

def find_materials_in_active(session, tracker):
    ao = bpy.context.active_object
    if ao is None:
        materials = []
    else:
        materials = find_materials_in_blob(ao)
    return set(materials)

def find_materials(session, preferences):
    if session.show_all:
        materials = find_materials_in_file(session)
    else:
        materials = find_materials_in_active(session, preferences.trackers_material)
    return materials

class ARK_OT_GoToMaterial(bpy.types.Operator):
    bl_idname = f"{addon.name}.go_to_material"
    bl_label = ""
    bl_options = {'INTERNAL'}

    name : bpy.props.StringProperty()

    def execute(self, context):
        preferences = addon.preferences
        session = addon.session
        material = bpy.data.materials.get(self.name)

        context.space_data.pin = False
        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

        tracker = utils.bpy.obj.obt(preferences.trackers_material, parent=context.scene.collection, hollow=True, force=True)
        tracker.use_fake_user = True
        tracker.hide_select = True
        tracker.hide_viewport = True

        if context.view_layer.objects.active is not None and context.view_layer.objects.active != tracker:
            session.last_obj = context.view_layer.objects.active.name

        context.view_layer.objects.active = tracker
        tracker.data.materials.clear()
        tracker.data.materials.append(material)
        session.current_blmat = material.name

        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
        context.space_data.pin = True

        if session.last_obj in context.view_layer.objects:
            context.view_layer.objects.active = utils.bpy.obj.obt(session.last_obj)
        else:
            context.view_layer.objects.active = None
        return {'INTERFACE'}

class ARK_PT_Materials(bpy.types.Panel):
    bl_label = "Catalog"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Material Catalog"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'NODE_EDITOR' and
            context.space_data.tree_type == 'ShaderNodeTree' and
            context.space_data.shader_type == 'OBJECT',)

    def draw(self, context):
        layout = self.layout
        session = addon.session
        preferences = addon.preferences
        materials = find_materials(session, preferences)


        col = layout.column(align=True)
        header = col.box().row()
        left = header.row()
        right = header.row(align=True)
        right.alignment = 'RIGHT'
        body = col.box()

        sub = left.row(align=True)
        sub.prop(session, "show_all", text="", icon='FILE_BACKUP')
        _ = sub.row(align=True)
        if not session.show_all:
            _.enabled = False
        _.prop(session, "show_orphan", text="", icon='ORPHAN_DATA')
        _.prop(session, "show_hidden", text="", icon='GHOST_ENABLED')

        right.prop(context.space_data, "pin", text="")

        column = body.column()
        if materials:
            for material in materials:
                is_current = (material.name == session.current_blmat)

                row = column.row(align=True)
                row.alert = (material.users == 0)
                opr = row.operator(
                    ARK_OT_GoToMaterial.bl_idname,
                    text = material.name,
                    emboss = is_current,
                    depress = is_current,
                )
                opr.name = material.name
        else:
            column.label(text="")
        return None

@addon.property
class WindowManager_Materials_Catalog(bpy.types.PropertyGroup):
    show_all : bpy.props.BoolProperty(
        name="Show All",
        default=True,
    )

    show_orphan : bpy.props.BoolProperty(
        name="Show Orphan",
        default=True,
    )

    show_hidden : bpy.props.BoolProperty(
        name="Show Hidden",
        default=True,
    )

    last_obj : bpy.props.StringProperty(
        name="Last Valid Object",
        default="",
    )

    current_blmat : bpy.props.StringProperty(
        name="Current Material",
        default="",
    )

@addon.property
class Preferences_Materials_Catalog(bpy.types.PropertyGroup):
    trackers_material : bpy.props.StringProperty(
        name="Material Tracker",
        default="#MaterialTracker",
    )

def UI(preferences, layout):
    layout.prop(preferences, "trackers_material")
    return None

CLASSES = [
    ARK_PT_Materials,
    ARK_OT_GoToMaterial,
    WindowManager_Materials_Catalog,
    Preferences_Materials_Catalog,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
