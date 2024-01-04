# SPDX-License-Identifier: GPL-2.0-or-later
import json
import zlib
import base64

import bpy
import mathutils

from ark import utils
formatter = utils.formatter()
pprint = formatter.print

from .common import RESERVED, BL_MAP, BL_DEFAULTS, type_from_bl_prop

DEBUG = print

global py_blend

def import_str(bl_prop, bl_parent, key, py_prop):
    setattr(bl_parent, key, str(py_prop))
    return None

def import_float(bl_prop, bl_parent, key, py_prop):
    if isinstance(py_prop, float):
        setattr(bl_parent, key, float(py_prop))
    elif isinstance(py_prop, list):
        setattr(bl_parent, key, [float(value) for value in py_prop])
    else:
        raise ValueError(bl_prop, bl_parent, py_prop, type(py_prop))
    return None

def import_int(bl_prop, bl_parent, key, py_prop):
    if isinstance(py_prop, int):
        setattr(bl_parent, key, int(py_prop))
    elif isinstance(py_prop, list):
        setattr(bl_parent, key, [int(value) for value in py_prop])
    else:
        raise ValueError(bl_prop, bl_parent, py_prop, type(py_prop))
    return None

def import_bool(bl_prop, bl_parent, key, py_prop):
    if isinstance(py_prop, bool):
        setattr(bl_parent, key, bool(py_prop))
    elif isinstance(py_prop, list):
        setattr(bl_parent, key, [bool(value) for value in py_prop])
    else:
        try:
            setattr(bl_parent, key, bool(py_prop))
        except:
            raise ValueError(bl_prop, bl_parent, py_prop, type(py_prop))
    return None

def import_collection_property(bl_prop, bl_parent, key, py_parent):
    t_fixed = type_from_bl_prop(bl_prop.fixed_type)
    t_parent = type_from_bl_prop(bl_parent.bl_rna)
    attr = getattr(bl_parent, key)

    if t_fixed in ATOMIC:
        PARSER = ATOMIC[t_fixed]
    elif t_fixed in COMPOSED:
        PARSER = COMPOSED[t_fixed]
    else:
        PARSER = import_py_rna

    match BL_MAP[t_parent][key]:
        case 'C_DICT':
            for id, py_prop in py_parent.items():
                PARSER(bl_prop, attr, id, py_prop)
        case 'C_LIST':
            if len(attr) > 0:
                for id, py_prop in enumerate(py_parent):
                    PARSER(bl_prop, attr, id, py_prop)
        case _:
            raise ValueError(bl_prop, key, t_fixed)
    return None

def import_py_rna(bl_prop, bl_parent, id, py_prop):
    match type(bl_prop):
        case bpy.types.CollectionProperty | bpy.types.PointerProperty:
            t = type_from_bl_prop(bl_prop.fixed_type)
        case _:
            t = type_from_bl_prop(bl_prop)

    if isinstance(id, int):
        attr = bl_parent[id]
    elif isinstance(id, str):
        attr = getattr(bl_parent, id)
    else:
        raise ValueError(bl_parent, id, type(id))

    if hasattr(attr, 'bl_rna'):
        for key in py_prop:
            if key in attr.bl_rna.properties.keys() and key not in RESERVED:
                attr_prop = attr.bl_rna.properties[key]
                t = type(attr_prop)
                if t in ATOMIC:
                    if not attr_prop.is_readonly or type(bl_prop) == bpy.types.PointerProperty:
                        ATOMIC[t](attr_prop, attr, key, py_prop[key])
                elif t == bpy.types.PointerProperty:
                    import_py_rna(attr_prop, attr, key, py_prop[key])
                else:
                    raise ValueError(key, bl_prop)
    else:
        DEBUG("!!! SKIP", key, attr, t)
    return None

def import_py_props(bl_parent, py_prop):
    FILTER = BL_MAP[type_from_bl_prop(bl_parent)]
    for key in py_prop:
        if key in bl_parent.bl_rna.properties.keys():
            attr_prop = bl_parent.bl_rna.properties[key]
            t = type(attr_prop)
            match FILTER[key]:
                case None:
                    if t in ATOMIC and not attr_prop.is_readonly:
                        ATOMIC[t](attr_prop, bl_parent, key, py_prop[key])
                case 'P_VALUE':
                    t_fixed = type(attr_prop.fixed_type)
                    if t_fixed in ATOMIC and not attr_prop.is_readonly:
                        ATOMIC[t_fixed](attr_prop, bl_parent, key, py_prop[key])
                    elif t_fixed in COMPOSED:
                        COMPOSED[t_fixed](attr_prop, bl_parent, key, py_prop[key])
                    else:
                        import_py_rna(attr_prop, bl_parent, key, py_prop[key])
                case 'C_LIST':
                    ATOMIC[t](attr_prop, bl_parent, key, py_prop[key])
                case _:
                    pass
    return None

def import_material(_, __, key, py_prop):
    bl_mat = utils.bpy.obt(bpy.data.materials, py_prop["name"], force=True, overwrite='HARD')
    bl_mat.use_nodes = True
    bl_mat.node_tree.nodes.clear()

    import_py_props(bl_mat, py_prop)
    return None

def import_node(bl_ntree, py_node):
    bl_node = bl_ntree.nodes.new(py_node["bl_idname"])
    #TODO: figure why name is not being applied by import_py_props()
    import_str(None, bl_node, "name", py_node["name"])
    match py_node["bl_idname"]:
        case 'NodeFrame':
            return None
        case 'NodeReroute':
            import_float(None, bl_node, "location", py_node["location"])
            return bl_node
        case 'ShaderNodeGroup':
            bl_node.node_tree = import_nodegroup(bl_ntree.nodes, None, py_node)
        case _:
            pass
    import_py_props(bl_node, py_node)
    return None

def import_nodetree(_, bl_parent, __, py_prop):
    bl_ntree = bl_parent.node_tree
    bl_nodes = bl_ntree.nodes

    #TODO: figure how node location works with frames
    # in_frame = []
    for py_node in py_prop["nodes"].values():
        import_node(bl_ntree, py_node)
    #     if "parent" in py_node:
    #         in_frame.append(py_node)

    # for py_node in in_frame:
    #     bl_nodes[py_node["name"]].parent = bl_nodes[py_node["parent"]]

    for py_link in py_prop["links"]:
        py_from = py_link["from_socket"]
        bl_from = bl_ntree.nodes[py_from[0]].outputs[py_from[1]]

        py_to = py_link["to_socket"]
        bl_to = bl_ntree.nodes[py_to[0]].inputs[py_to[1]]

        bl_ntree.links.new(bl_from, bl_to)
    return None

def import_nodegroup(_, __, py_prop):
    global py_blend
    bl_ntree = utils.bpy.obt(bpy.data.node_groups, py_prop["node_tree"], type='ShaderNodeTree', force=True, overwrite='NEW')
    bl_nodes = bl_ntree.nodes
    py_ntree = py_blend["node_groups"][py_prop["node_tree"]]

    bl_interface = bl_ntree.interface

    for py_socket in py_ntree["interface"]["items_tree"]:
        match py_socket["item_type"]:
            case 'SOCKET':
                in_out = py_socket["in_out"] if "in_out" in py_socket else 'INPUT'
                socket_type = py_socket["socket_type"] if "socket_type" in py_socket else 'NodeSocketFloat'
                # ^^ This is caused by 3.0 to 4.0 bad conversion ^^
                bl_interface.new_socket(name=py_socket["name"], in_out=in_out, socket_type=socket_type)
            case 'PANEL':
                pass
            case _:
                pass

    #TODO: figure how node location works with frames
    # in_frame = []
    for py_node in py_ntree["nodes"].values():
        import_node(bl_ntree, py_node)
    #     if "parent" in py_node:
    #         in_frame.append(py_node)

    # for py_node in in_frame:
    #     bl_nodes[py_node["name"]].parent = bl_nodes[py_node["parent"]]

    for py_link in py_ntree["links"]:
        py_from = py_link["from_socket"]
        bl_from = bl_nodes[py_from[0]].outputs[py_from[1]]

        py_to = py_link["to_socket"]
        bl_to = bl_nodes[py_to[0]].inputs[py_to[1]]

        bl_ntree.links.new(bl_from, bl_to)
    return bl_ntree

def import_curve_map(_, bl_parent, key, py_prop):
    bl_points = getattr(bl_parent[key], "points")
    _len = len(bl_points)
    for id, py_point in enumerate(py_prop["points"]):
        if id < _len:
            bl_point = bl_points[id]
            import_float(None, bl_point, "location", py_point["location"])
            import_str(None, bl_point, "handle_type", py_point["handle_type"])
        else:
            bl_point = bl_points.new(py_point["location"][0], py_point["location"][1])
            import_str(None, bl_point, "handle_type", py_point["handle_type"])
    return None

BLEND_ID_DATA = {
    bpy.types.NodeTree : 'node_groups',
}

ATOMIC = {
    bpy.types.EnumProperty : import_str,
    bpy.types.StringProperty : import_str,
    bpy.types.BoolProperty : import_bool,
    bpy.types.IntProperty : import_int,
    bpy.types.FloatProperty : import_float,
    bpy.types.CollectionProperty : import_collection_property,
}

COMPOSED = {
    bpy.types.Material : import_material,
    bpy.types.NodeTree : import_nodetree,
    bpy.types.CurveMap : import_curve_map,
}

def import_py_blend(py_blend):
    bl_parent = bpy.data
    for key in py_blend:
        bl_prop = bpy.data.bl_rna.properties[key]
        t = type(bl_prop)
        if t == bpy.types.CollectionProperty and key == 'materials':
            import_collection_property(bl_prop, bl_parent, key, py_blend[key])
    return None

def uncompress(encoded):
    compressed = base64.b64decode(encoded)
    json_str = zlib.decompress(compressed).decode('utf8')
    return json.loads(json_str)

class ARK_OT_IOJSON_ImportClipboard(bpy.types.Operator):
    bl_idname = "ark.iojson_import_clipboard"
    bl_label = "Import JSON"

    def execute(self, context):
        global py_blend
        py_blend = uncompress(bpy.context.window_manager.clipboard)
        import_py_blend(py_blend)
        return {'FINISHED'}

    @staticmethod
    def button(self, context):
        self.layout.operator(ARK_OT_IOJSON_ImportClipboard.bl_idname, text=ARK_OT_IOJSON_ImportClipboard.bl_label)
        return None

def register():
    bpy.utils.register_class(ARK_OT_IOJSON_ImportClipboard)
    bpy.types.CONSOLE_HT_header.append(ARK_OT_IOJSON_ImportClipboard.button)
    return None

def unregister():
    bpy.types.CONSOLE_HT_header.remove(ARK_OT_IOJSON_ImportClipboard.button)
    bpy.utils.unregister_class(ARK_OT_IOJSON_ImportClipboard)
    return None