# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
import inspect
import os
import sys

from .. import std

properties = {}

class _Caller():
    def __init__(self):
        frame = inspect.currentframe()
        try:
            self.frame = frame.f_back.f_back
            self.mod = inspect.getmodule(self.frame)
            split = self.mod.__name__.split(".")
            self.path = ".".join(split)
            self.subpath = ".".join(split[1:])
            self.name = split.pop()
            self.parent = ".".join(split)
        finally:
            del frame
        return None

# CREDIT: https://blender.stackexchange.com/questions/227358#227402
class Addon:
    def __init__(self, **kwargs):
        self.caller = _Caller()
        self.name = self.caller.mod.__name__.split(".", 1)[0]
        return None

    @property
    def preferences(self, root=False):
        """bpy.context.preferences.addons[demo].preferences"""
        if root:
            return bpy.context.preferences.addons[self.name].preferences
        else:
            return std.rgetattr(bpy.context.preferences.addons[self.name].preferences, self.caller.subpath)

    @property
    def session(self, root=False):
        """bpy.context.window_manager.demo"""
        if root:
            return getattr(bpy.context.window_manager, self.name, None)
        else:
            return std.rgetattr(bpy.context.window_manager, self.caller.path)

    # CREDIT: https://github.com/nutti/Screencast-Keys/commit/51925cbe31045eeeb7283c88b6c01d3ef1df2c2d
    def property(self, cls):
        """Generates PropertyGroup from child modules (if any). And adds itself
        to parent key in {properties} dictionary.
        """
        parent_module = self.caller.parent
        module = self.caller.path
        kind = cls.__name__.split("_")[1]

        if kind not in properties:
            properties.update({kind : {}})

        # Generate child modules' reference
        if module in properties[kind]:
            for child in properties[kind][module]:
                attr = child.__module__.split(".")[-1]
                cls.__annotations__[attr] = bpy.props.PointerProperty(type=child)

        # Add itself to parent key in dictionary
        if parent_module not in properties[kind]:
            properties[kind].update({parent_module : []})
        properties[kind][parent_module].append(cls)
        return cls

    def set_property(self, cls):
        kind = cls.__name__.split("_")[1]
        if kind == "Preferences":
            return None
        object = eval(f"bpy.types.{kind}")
        setattr(object, self.name, bpy.props.PointerProperty(type=cls))
        return None

    def set_properties(self, props):
        for cls in props:
            self.set_property(cls)
        return None

    def get_property(self, kind, root=False):
        object = getattr(bpy.context, kind)
        if root:
            return getattr(object, self.name, None)
        else:
            return std.rgetattr(object, self.caller.path)

    def del_property(self, cls):
        kind = cls.__name__.split("_")[1]
        if kind == "Preferences":
            return None
        location = cls.__name__.split("_")[1]
        object = eval(f"bpy.types.{kind}")
        delattr(object, self.name)
        return None

    def del_properties(self, props):
        for cls in reversed(props):
            self.del_property(cls)
        return None

def register_classes(classes):
    for cls in classes:
        bpy.utils.register_class(cls)
    return None

def unregister_classes(classes):
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    return None

def register_modules(modules):
    for module in modules.values():
        module.register()
    return None

def unregister_modules(modules):
    for module in modules.values():
        module.unregister()
    return None
