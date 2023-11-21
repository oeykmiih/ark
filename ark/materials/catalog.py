# SPDX-License-Identifier: GPL-2.0-or-later
import io
import contextlib

import bpy

from ark import utils
addon = utils.bpy.Addon()

class MaterialList():
    def __init__(self, session, preferences):
        self.session = session
        self.preferences = preferences
        self.blob = None
        self.materials = []
        self.checked_groups = []

    def get(self):
        if self.session.show_all:
            self.find_materials_in_file()
        else:
            self.active_object()
            self.find_materials_in_active()

        return self.materials

    def active_object(self):
        if not bpy.context.active_object:
            return None
        if bpy.context.active_object.name == self.preferences.trackers_material:
            self.blob = utils.bpy.obj.obt(self.session.last_obj, local=True)
        else:
            self.blob = bpy.context.active_object
            self.session.last_obj = self.blob.name
        return None

    def find_materials_in_active(self):
        if not self.blob:
            return None

        if self.blob.instance_type == 'COLLECTION' and self.blob.instance_collection is not None and self.blob.type == 'EMPTY':
            self.find_materials_in_instances(self.blob)
        else:
            self.find_materials_in_object(self.blob)
        return None

    def find_materials_in_file(self):
        for material in bpy.data.materials:
            if material.is_grease_pencil is False:
                if material.users > 0 or self.session.show_orphan:
                    if material not in self.materials:
                        if not material.name.startswith(".") or self.session.show_hidden:
                            self.materials.append(material)
        return None

    def find_materials_in_instances(self, empty):
        if empty.instance_collection.name in self.checked_groups:
            return None
        for blob in bpy.data.collections[empty.instance_collection.name].objects:
            if 'COLLECTION' and blob.instance_collection is not None and blob.type == 'EMPTY':
                self.find_materials_in_instances(blob)
            else:
                self.find_materials_in_object(blob)

        self.checked_groups.append(empty.instance_collection.name)
        return None

    def find_materials_in_object(self, blob):
        if blob.type == "MESH":
            for material in (slot.material for slot in blob.material_slots if slot.material is not None):
                if material not in self.materials:
                    if not material.name.startswith(".") or self.session.show_hidden:
                        self.materials.append(material)
        return None

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

        context.view_layer.objects.active = utils.bpy.obj.obt(session.last_obj)
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
        materials = MaterialList(session, preferences).get()


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

        left.row().prop(session, "show_hidden", text="", icon='GHOST_ENABLED')

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
