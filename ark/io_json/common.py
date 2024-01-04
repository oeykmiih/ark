# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

RESERVED = {
    'rna_type',
    'original',
    'id_data',
    'type',
    'bl_label',
}

BL_MAP = {
    # P_ suffix -> Pointer Property
    # C_ suffix -> Collection Property
    bpy.types.BlendData : {
        'materials' : 'C_DICT',
        'node_groups' : 'C_DICT',
        'version' : 'P_VALUE',
    },
    bpy.types.ColorRamp : {
        'color_mode' : None,
        'hue_interpolation' : None,
        'interpolation' : None,
        'elements' : 'C_LIST',
    },
    bpy.types.CurveMap : {
        'points' : 'C_LIST',
    },
    bpy.types.CurveMapping : {
        'curves' : 'C_LIST',
    },
    bpy.types.Material : {
        'name' : None,
        'cycles' : 'P_VALUE',
        'diffuse_color' : None,
        'metallic' : None,
        'node_tree' : 'P_VALUE',
        'pass_index' : None,
        'roughness' : None,
        # 'use_nodes' : None,
    },
    bpy.types.Node : {
        'air_density' : None,
        'altitude' : None,
        'attribute_name' : None,
        'attribute_type' : None,
        'axis' : None,
        'bands_direction' : None,
        'bl_idname' : None,
        'blend_type' : None,
        'bytecode_hash' : None,
        'bytecode' : None,
        'clamp_factor' : None,
        'clamp_result' : None,
        'clamp_type' : None,
        'clamp' : None,
        # 'color_mapping' : None,
        'color_ramp' : 'P_VALUE',
        'component' : None,
        'convert_from' : None,
        'convert_to' : None,
        'data_type' : None,
        'direction_type' : None,
        'distance' : None,
        'distribution' : None,
        'dust_density' : None,
        'extension' : None,
        'factor_mode' : None,
        'falloff' : None,
        'feature' : None,
        'filepath' : None,
        'from_instancer' : None,
        'gradient_type' : None,
        'grease_pencil' : None,
        'ground_albedo' : None,
        'hide' : None,
        'ies' : None,
        'image_user' : None,
        'image' : None,
        'inputs' : 'C_LIST',
        'inside' : None,
        'interface' : None,
        'interpolation_type' : None,
        'interpolation' : None,
        'invert' : None,
        'is_active_output' : None,
        'label' : None,
        'layer_name' : None,
        'location' : None,
        'mapping' : 'P_VALUE',
        'mode' : None,
        'model' : None,
        'musgrave_dimensions' : None,
        'musgrave_type' : None,
        'mute' : None,
        'name' : None,
        'node_tree' : 'P_DATA',
        'noise_dimensions' : None,
        'normalize' : None,
        'object' : None,
        'offset_frequency' : None,
        'offset' : None,
        'only_local' : None,
        'operation' : None,
        'outputs' : 'C_LIST',
        'ozone_density' : None,
        'parametrization' : None,
        'particle_color_source' : None,
        'particle_system' : None,
        'point_source' : None,
        'projection_blend' : None,
        'projection' : None,
        'radius' : None,
        'resolution' : None,
        'rings_direction' : None,
        'rotation_type' : None,
        'samples' : None,
        'script' : None,
        'show_options' : None,
        'show_preview' : None,
        'show_texture' : None,
        'sky_type' : None,
        'space' : None,
        'squash_frequency' : None,
        'squash' : None,
        'subsurface_method' : None,
        'sun_direction' : None,
        'sun_disc' : None,
        'sun_elevation' : None,
        'sun_intensity' : None,
        'sun_rotation' : None,
        'sun_size' : None,
        'target' : None,
        'texture_mapping' : None,
        'turbidity' : None,
        'turbulence_depth' : None,
        'use_alpha' : None,
        'use_auto_update' : None,
        'use_clamp' : None,
        'use_pixel_size' : None,
        'use_tips' : None,
        'uv_map' : None,
        'vector_type' : None,
        'vertex_attribute_name' : None,
        'vertex_color_source' : None,
        'view_center' : None,
        'voronoi_dimensions' : None,
        'wave_profile' : None,
        'wave_type' : None,
    },
    bpy.types.NodeSocket : {
        'name' : None,
        'bl_idname' : None,
        'bl_subtype_label' : None,
        'default_value' : None,
        'hide' : None,
        'hide_value' : None,
    },
    bpy.types.NodeTree : {
        'bl_idname' : 'P_VALUE',
        'nodes' : 'C_DICT',
        'links' : 'C_LIST',
        'name' : 'P_VALUE',
        'interface' : 'P_VALUE',
    },
    bpy.types.NodeLink : {
        'from_socket' : 'P_LOCAL',
        'to_socket' : 'P_LOCAL',
    },
    bpy.types.NodeTreeInterface : {
        'items_tree' : 'C_LIST',
        '' : None,
    },
    bpy.types.NodeTreeInterfaceItem : {
        'in_out' : None,
        'index' : None,
        'item_type' : None,
        'name' : None,
        'parent' : 'P_INDEX',
        'socket_type' : None,
        'subtype' : None,
    },
    bpy.types.NodeTreeInterfacePanel : {
        'index' : None,
        'name' : None,
    },
}

BL_DEFAULTS = {
    bpy.types.Material : {
        'name' : 'Shader Nodetree',
    },
}
for key in BL_MAP:
    if key not in BL_DEFAULTS:
        BL_DEFAULTS.update({key : {}})

def type_from_bl_prop(bl_prop):
    ts = type(bl_prop).__mro__
    if bpy.types.ID in ts:
        i = ts.index(bpy.types.ID)
    elif bpy.types.Property in ts:
        i = ts.index(bpy.types.Property)
    elif bpy.types.bpy_struct in ts:
        i = ts.index(bpy.types.bpy_struct)
    else:
        raise ValueError(bl_prop, ts)
    t = ts[i - 1]
    return t