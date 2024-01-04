# SPDX-License-Identifier: GPL-2.0-or-later
import json
import re
import zlib
import base64

import bpy
import mathutils

from ark import utils
formatter = utils.formatter()
pprint = formatter.print

from .common import BL_MAP, BL_DEFAULTS, RESERVED, type_from_bl_prop

DEBUG = print

global BLEND_ID_DATA
BLEND_ID_DATA = {}

DESTRUCTORS = {
    bpy.types.NodeSocket : lambda attr: [attr.node.name, int(re.findall(r"(\d+)\]$", attr.__repr__())[0])],
}

def parse_int(bl_prop, attr):
    if isinstance(attr, int):
        return attr
    elif bl_prop is None or bl_prop.array_length > 0:
        return [parse_int(None, value) for value in attr]

def parse_float(bl_prop, attr):
    if isinstance(attr, float):
        return round(attr, 5)
    elif bl_prop is None or bl_prop.array_length > 0:
        return [parse_float(None, value) for value in attr]

def parse_bool(bl_prop, attr):
    if isinstance(attr, bool):
        return round(attr, 5)
    elif bl_prop is None or bl_prop.array_length > 0:
        return [parse_bool(None, value) for value in attr]

def parse_str(bl_prop, attr):
    # DOC: https://docs.blender.org/api/main/bpy_types_enum_items/property_subtype_string_items.html
    match bl_prop.subtype:
        case 'DIR_PATH' | 'FILE_PATH' | 'FILE_NAME':
            return bpy.path.abspath(attr)
        case 'NONE' | 'PASSWORD' | 'PIXEL':
            return attr
        case 'BYTE_STRING':
            return attr.decode
        case _:
            raise ValueError(bl_prop, attr, bl_prop.subtype)

def parse_collection_property(bl_prop, attr, mode='C_LIST'):
    t_fixed = type_from_bl_prop(bl_prop.fixed_type)
    match mode:
        case 'C_LIST':
            if t_fixed not in ATOMIC:
                return [parse_bl_rna(item) for item in attr]
            else:
                return [ATOMIC[item] for item in attr]
        case 'C_DICT':
            if t_fixed not in ATOMIC:
                return {item.name : parse_bl_rna(item) for item in attr}
            else:
                return {item.name : ATOMIC[item] for item in attr}
        case _:
            raise ValueError(bl_prop, attr, mode, t_fixed)

def parse_pointer(bl_prop, attr):
    t = type_from_bl_prop(bl_prop.fixed_type)

    if t not in ATOMIC:
        return parse_bl_rna(attr)
    else:
        return ATOMIC[t](attr)

def parse_bl_rna(bl_parent, *args):
    def _add(attr, key, bl_prop, py_parent, filter):
        if attr is not None:
            t = type(bl_prop)
            match t:
                case bpy.types.StringProperty|bpy.types.EnumProperty:
                    if attr not in {"", "NONE", "None"}:
                        py_parent[key] = ATOMIC[t](bl_prop, attr)
                case bpy.types.PointerProperty:
                    mode = filter[key]
                    match mode:
                        case 'P_VALUE':
                            py_parent[key] = parse_pointer(bl_prop, attr)
                        case 'P_INDEX':
                            py_parent[key] = attr.index
                        case 'P_NAME':
                            py_parent[key] = attr.name
                        case 'P_DATA':
                            t = type_from_bl_prop(attr)
                            queue_bl_id_data(attr, BLEND_ID_DATA[t])
                            py_parent[key] = attr.name
                        case 'P_LOCAL':
                            t = type_from_bl_prop(attr)
                            py_parent[key] = DESTRUCTORS[t](attr)
                        case _:
                            raise ValueError(key, bl_parent, mode, attr)
                case bpy.types.CollectionProperty:
                    mode = filter[key]
                    py_parent[key] = ATOMIC[t](bl_prop, attr, mode=mode)
                case _:
                    py_parent[key] = ATOMIC[t](bl_prop, attr)
        return None

    global BLEND_ID_DATA
    t = type_from_bl_prop(bl_parent)
    FILTER = BL_MAP[t] if t in BL_MAP else {key : None for key in bl_parent.bl_rna.properties.keys() if key not in RESERVED}
    DEFAULT = BL_DEFAULTS[t] if t in BL_DEFAULTS else {}

    py_parent = {}
    for key, bl_prop in bl_parent.bl_rna.properties.items():
        if key in FILTER:
            if hasattr(bl_parent, key):
                attr = getattr(bl_parent, key)
                # if not hasattr(bl_prop, "default") or attr != bl_prop.default:
                if key not in DEFAULT or attr != DEFAULT[key]:
                    _add(attr, key, bl_prop, py_parent, FILTER)
    return py_parent

ATOMIC = {
    bpy.types.EnumProperty : parse_str,
    bpy.types.StringProperty : parse_str,
    bpy.types.BoolProperty : parse_bool,
    bpy.types.IntProperty : parse_int,
    bpy.types.FloatProperty : parse_float,
    bpy.types.PointerProperty : parse_pointer,
    bpy.types.CollectionProperty : parse_collection_property,
    bpy.types.PropertyGroup : parse_bl_rna,
    None : None,
}

def queue_bl_id_data(bl_prop, idt):
    global py_blend
    py_idt = py_blend[idt]
    name = bl_prop.name
    if name not in py_idt:
        py_blend[idt][bl_prop.name] = parse_bl_rna(bl_prop)
    return None

def init_py_blend():
    global BLEND_ID_DATA
    for key in BL_MAP[bpy.types.BlendData]:
        bl_prop = bpy.data.bl_rna.properties[key]
        if type(bl_prop) == bpy.types.CollectionProperty:
            BLEND_ID_DATA[type(bpy.data.bl_rna.properties[key].fixed_type)] = key
    global py_blend
    py_blend = {}
    for idt in BL_MAP[bpy.types.BlendData]:
        py_blend[idt] = {}
    return py_blend

def compress(py_dict):
    json_str = json.dumps(py_dict, separators=(',', ':')).encode("utf8")
    compressed = zlib.compress(json_str, 9)
    encoded = base64.b64encode(compressed).decode()
    return encoded

class ARK_OT_IOJSON_ExportClipboard(bpy.types.Operator):
    bl_idname = "ark.iojson_export_clipboard"
    bl_label = "Export JSON"

    def execute(self, context):
        py_blend = init_py_blend()
        py_blend = parse_bl_rna(bpy.data)

            file.write(json.dumps(py_blend))
        bpy.context.window_manager.clipboard = compress(py_blend)
        return {'FINISHED'}

    @staticmethod
    def button(self, context):
        self.layout.operator(ARK_OT_IOJSON_ExportClipboard.bl_idname, text=ARK_OT_IOJSON_ExportClipboard.bl_label)
        return None

def register():
    bpy.utils.register_class(ARK_OT_IOJSON_ExportClipboard)
    bpy.types.CONSOLE_HT_header.append(ARK_OT_IOJSON_ExportClipboard.button)
    bpy.types.NODE_MT_context_menu.append(ARK_OT_IOJSON_ExportClipboard.button)
    return None

def unregister():
    bpy.types.NODE_MT_context_menu.remove(ARK_OT_IOJSON_ExportClipboard.button)
    bpy.types.CONSOLE_HT_header.remove(ARK_OT_IOJSON_ExportClipboard.button)
    bpy.utils.unregister_class(ARK_OT_IOJSON_ExportClipboard)
    return None