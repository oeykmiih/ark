# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import bl_ui
import importlib
import json

from ark import utils
addon = utils.bpy.Addon()

from . import enums

class ARK_PT_Hide(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"
    bl_label = ""
    bl_context = "texture"

    def draw(self, context):
        self.layout.label(text="Text")
        return None
    pass

def rsearch(keywords, tree):
    found = []
    for id in keywords:
        yield from _search(id, tree)
    return None

def _search(id, tree):
    if id in tree:
        for child in tree[id]:
            yield from _search(child, tree)
        yield id
        del tree[id]
    return None

def build_tree():
    tree = {}
    for id in dir(bpy.types):
        cls = getattr(bpy.types, id)
        if id not in tree:
            tree[id] = []
        if hasattr(cls, "bl_parent_id"):
            parent = cls.bl_parent_id
            if parent not in tree:
                tree[parent] = []
            tree[parent].append(id)
    return tree

def enable():
    session = addon.session
    ids = rsearch(enums.UI_TO_HIDE, build_tree())
    restore = {}
    addresses = {}

    for name in ids:
        cls = getattr(bpy.types, name)
        parent = getattr(cls, "bl_parent_id", None)
        module = cls.__module__

        bpy.utils.unregister_class(cls)

        addresses[name] = module

    session.addresses = json.dumps(addresses)
    return None

def disable():
    session = addon.session
    if not hasattr(session, "addresses"):
        return None
    addresses = json.loads(session.addresses)
    session.addresses = ""

    for id, module in reversed(addresses.items()):
        module = importlib.import_module(module)
        cls = getattr(module, id)
        if not cls.is_registered:
            bpy.utils.register_class(cls)
    return None

@addon.property
class WindowManager_Interface_Hide(bpy.types.PropertyGroup):
    def update_toggle(self, context):
        if self.toggle:
            enable()
        else:
            disable()
        return None

    toggle : bpy.props.BoolProperty(
        name = "Toogle",
        default = False,
        update = update_toggle,
    )

    addresses : bpy.props.StringProperty(
        name = "Adresses",
        default = "",
    )

@addon.property
class Preferences_Interface_Hide(bpy.types.PropertyGroup):
    pass

CLASSES = [
    ARK_PT_Hide,
    WindowManager_Interface_Hide,
    Preferences_Interface_Hide,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None
