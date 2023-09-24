# SPDX-License-Identifier: GPL-2.0-or-later
EDITOR_TYPE = [
    ('VIEW_3D', "VIEW_3D", ""),
    ('IMAGE_EDITOR', "IMAGE_EDITOR", ""),
    ('UV', "UV", ""),
    ('CompositorNodeTree', "CompositorNodeTree", ""),
    ('TextureNodeTree', "TextureNodeTree", ""),
    ('GeometryNodeTree', "GeometryNodeTree", ""),
    ('ShaderNodeTree', "ShaderNodeTree", ""),
    ('SEQUENCE_EDITOR', "SEQUENCE_EDITOR", ""),
    ('CLIP_EDITOR', "CLIP_EDITOR", ""),
    ('DOPESHEET', "DOPESHEET", ""),
    ('TIMELINE', "TIMELINE", ""),
    ('FCURVES', "FCURVES", ""),
    ('DRIVERS', "DRIVERS", ""),
    ('NLA_EDITOR', "NLA_EDITOR", ""),
    ('TEXT_EDITOR', "TEXT_EDITOR", ""),
    ('CONSOLE', "CONSOLE", ""),
    ('INFO', "INFO", ""),
    ('OUTLINER', "OUTLINER", ""),
    ('PROPERTIES', "PROPERTIES", ""),
    ('FILES', "FILES", ""),
    ('ASSETS', "ASSETS", ""),
    ('SPREADSHEET', "SPREADSHEET", ""),
    ('PREFERENCES', "PREFERENCES", ""),
]

EDITOR_TYPE_ICONS = {
    'ASSETS' : 'ASSET_MANAGER',
    'OUTLINER' : 'OUTLINER',
    'PROPERTIES' : 'PROPERTIES',
    'ShaderNodeTree' : 'MATERIAL',
    'VIEW_3D' : 'VIEW3D',
}

EDITOR_MODE_ICONS = {
    'ASSETS' : {
        'MATERIAL' : 'NODE_MATERIAL',
        'MODELS' : 'SNAP_VOLUME',
        'NODETREE' : 'NODETREE',
    },
    'OUTLINER' : {
        'VIEW_LAYER' : 'RENDERLAYERS',
        'FILE' : 'FILE_BLEND',
        'FILE_MATERIAL' : 'MATERIAL',
        'FILE_NODETREE' : 'NODETREE',
        'ORPHAN' : 'ORPHAN_DATA',
        'ORPHAN_MATERIAL' : 'MATERIAL',
        'ORPHAN_NODETREE' : 'NODETREE',
    },
    'PROPERTIES' : {
    },
    'ShaderNodeTree' : {
        'OBJECT' : 'OBJECT_DATAMODE',
        'WORLD' : 'WORLD',
    },
    'VIEW_3D' : {
        'RENDERED' : 'SHADING_RENDERED',
        'SOLID' : 'SHADING_SOLID',
        'WIREFRAME' : 'SHADING_WIRE',
    },
}

EDITOR_MODE = {
    'OUTLINER' : {
        'VIEW_LAYER' : {
            "context.space_data.display_mode" : 'VIEW_LAYER',
        },
        'FILE' : {
            "context.space_data.display_mode" : 'LIBRARIES',
            "context.space_data.use_filter_id_type" : False,
        },
        'FILE_MATERIAL' : {
            "context.space_data.display_mode" : 'LIBRARIES',
            "context.space_data.use_filter_id_type" : True,
            "context.space_data.filter_id_type" : 'MATERIAL',
        },
        'FILE_NODETREE' : {
            "context.space_data.display_mode" : 'LIBRARIES',
            "context.space_data.use_filter_id_type" : True,
            "context.space_data.filter_id_type" : 'NODETREE',
        },
        'ORPHAN' : {
            "context.space_data.display_mode" : 'ORPHAN_DATA',
            "context.space_data.use_filter_id_type" : False,
        },
        'ORPHAN_MATERIAL' : {
            "context.space_data.display_mode" : 'ORPHAN_DATA',
            "context.space_data.use_filter_id_type" : True,
            "context.space_data.filter_id_type" : 'MATERIAL',
        },
        'ORPHAN_NODETREE' : {
            "context.space_data.display_mode" : 'ORPHAN_DATA',
            "context.space_data.use_filter_id_type" : True,
            "context.space_data.filter_id_type" : 'NODETREE',
        },
    },
    'PROPERTIES' : {
    },
    'ASSETS' : {
        'MATERIAL' : {
            "context.space_data.params.filter_id.filter_action" : False,
            "context.space_data.params.filter_id.filter_group" : False,
            "context.space_data.params.filter_id.filter_material" : False,
            "context.space_data.params.filter_id.filter_node_tree" : True,
            "context.space_data.params.filter_id.filter_object" : False,
            "context.space_data.params.filter_id.filter_world" : False,
        },
        'MODELS' : {
            "context.space_data.params.filter_id.filter_action" : False,
            "context.space_data.params.filter_id.filter_group" : True,
            "context.space_data.params.filter_id.filter_material" : False,
            "context.space_data.params.filter_id.filter_node_tree" : False,
            "context.space_data.params.filter_id.filter_object" : True,
            "context.space_data.params.filter_id.filter_world" : False,
        },
    },
    'ShaderNodeTree' : {
        'OBJECT' : {
            "context.space_data.shader_type" : 'OBJECT',
        },
        'WORLD' : {
            "context.space_data.shader_type" : 'WORLD',
        },
    },
    'VIEW_3D' : {
        'WIREFRAME' : {
            "context.space_data.shading.type" : 'WIREFRAME',
        },
        'SOLID' : {
            "context.space_data.shading.type" : 'SOLID',
        },
        'RENDERED' : {
            "context.space_data.shading.type" : 'RENDERED',
        },
    },
}

UI_TO_HIDE = [
# Properties Render
    # "CYCLES_RENDER_PT_sampling",
    "CYCLES_RENDER_PT_sampling_lights",
    "CYCLES_RENDER_PT_sampling_advanced",
    # "CYCLES_RENDER_PT_light_paths",
    "CYCLES_RENDER_PT_volumes",
    "CYCLES_RENDER_PT_subdivision",
    "CYCLES_RENDER_PT_curves",
    "CYCLES_RENDER_PT_simplify",
    "RENDER_PT_simplify",
    # "CYCLES_VIEW3D_PT_simplify_greasepencil", # Not coded the same way?
    "CYCLES_RENDER_PT_motion_blur",
    "CYCLES_RENDER_PT_film",
    # "CYCLES_RENDER_PT_film_pixel_filter",
    "CYCLES_RENDER_PT_performance",
    "CYCLES_RENDER_PT_bake",
    "RENDER_PT_gpencil",
    "RENDER_PT_freestyle",
    # "RENDER_PT_color_management",
# Properties Output
    "RENDER_PT_format",
    "RENDER_PT_frame_range",
    "RENDER_PT_time_stretching",
    "RENDER_PT_stereoscopy",
    # "RENDER_PT_output",
    "RENDER_PT_stamp",
    "RENDER_PT_stamp_note",
    "RENDER_PT_stamp_burn",
    "RENDER_PT_post_processing",
    "CYCLES_PT_post_processing",
# Properties View Layer
    "VIEWLAYER_PT_layer",
    # "CYCLES_RENDER_PT_passes",
    "CYCLES_RENDER_PT_filter",
    "CYCLES_RENDER_PT_override",
# Properties Scene
    "SCENE_PT_scene",
    "SCENE_PT_unit",
    "SCENE_PT_physics",
    "SCENE_PT_keying_sets",
    "SCENE_PT_audio",
    "SCENE_PT_rigid_body_world",
    "SCENE_PT_custom_props",
# Properties World
    "CYCLES_WORLD_PT_preview",
    "CYCLES_WORLD_PT_surface",
    "CYCLES_WORLD_PT_volume",
    "CYCLES_WORLD_PT_ray_visibility",
    "CYCLES_WORLD_PT_settings",
    "WORLD_PT_viewport_display",
    "WORLD_PT_custom_props",
# Properties Object
    "OBJECT_PT_collections",
    "OBJECT_PT_constraints",
    "OBJECT_PT_delta_transform",
    "OBJECT_PT_instancing",
    "OBJECT_PT_lineart",
    "OBJECT_PT_motion_paths",
    "OBJECT_PT_relations",
# Properties Material
    "MATERIAL_PT_preview",
    "MATERIAL_PT_lineart    ",
# # View3D Header
    # "VIEW3D_MT_view",
    # "VIEW3D_MT_select_object",
    # "VIEW3D_MT_add",
    # "VIEW3D_MT_object",
    # "VIEW3D_PT_object_type_visibility",
    # "VIEW3D_PT_transform_orientations",
# View3D Toolbar
    "VIEW3D_PT_active_tool",
    "VIEW3D_PT_collections",
    "VIEW3D_PT_tools_object_options",
    "WORKSPACE_PT_main",
    "WORKSPACE_PT_addons",
    "VIEW3D_PT_grease_pencil",
    "VIEW3D_PT_view3d_cursor",
    "VIEW3D_PT_view3d_properties",
# ShaderEditor Toolbar
    "NODE_PT_active_tool",
    # "NODE_MATERIAL_PT_viewport",
    # "NODE_PT_active_node_generic",
    # "NODE_PT_active_node_color",
    # "NODE_PT_active_node_properties",
    "NODE_PT_annotation",
    # "NODE_CYCLES_MATERIAL_PT_settings",
    # "NODE_DATA_PT_light",
]
