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
    'ShaderNodeTree' : 'NODE_MATERIAL',
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
        'NODETREE' : {
            "context.space_data.params.filter_id.filter_action" : False,
            "context.space_data.params.filter_id.filter_group" : False,
            "context.space_data.params.filter_id.filter_material" : False,
            "context.space_data.params.filter_id.filter_node_tree" : True,
            "context.space_data.params.filter_id.filter_object" : False,
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
    },
}
