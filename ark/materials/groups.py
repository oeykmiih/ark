# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from ark import utils
addon = utils.bpy.Addon()

class ARK_OT_PurgeDuplicatedNodeGroups(bpy.types.Operator):
    bl_idname = f"{addon.name}.purge_duplicated_nodegroups"
    bl_label = "Purge Duplicated NodeGroups"

    def execute(self, context):
        for ngroup in bpy.data.node_groups:
            base, sep, ext = ngroup.name.rpartition('.')

            if ext.isnumeric():
                if base in bpy.data.node_groups:
                    ngroup.use_fake_user = False
                    ngroup.user_remap(bpy.data.node_groups[base])
                    bpy.data.node_groups.remove(ngroup)
                else:
                    ngroup.name = base
        return {'FINISHED'}

class ARK_OT_PushNodeGroupValues(bpy.types.Operator):
    bl_idname = f"{addon.name}.push_nodegroup_values"
    bl_label = "Push NodeGroups Values"

    @classmethod
    def poll(cls, context):
        for node in context.selected_nodes:
            if node.bl_idname == 'ShaderNodeGroup':
                return True
        else:
            return False

    def execute(self, context):
        for node in context.selected_nodes:
            if node.bl_idname == 'ShaderNodeGroup':
                i = 0
                for item in node.node_tree.interface.items_tree:
                    if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                        item.default_value = node.inputs[i].default_value
                        i += 1
        return {'FINISHED'}

class ARK_OT_ResetNodeGroupValues(bpy.types.Operator):
    bl_idname = f"{addon.name}.reset_nodegroup_values"
    bl_label = "Reset NodeGroups Values"

    @classmethod
    def poll(cls, context):
        for node in context.selected_nodes:
            if node.bl_idname == 'ShaderNodeGroup':
                return True
        else:
            return False

    def execute(self, context):
        for node in context.selected_nodes:
            if node.bl_idname == 'ShaderNodeGroup':
                ntree_inputs = []
                for item in node.node_tree.interface.items_tree:
                    if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                        ntree_inputs.append(item.default_value)

                for i, input in enumerate(node.inputs):
                    input.default_value = ntree_inputs[i]
        return {'FINISHED'}

CLASSES = [
    ARK_OT_PurgeDuplicatedNodeGroups,
    ARK_OT_PushNodeGroupValues,
    ARK_OT_ResetNodeGroupValues,
]

def register():
    utils.bpy.register_classes(CLASSES)
    return None

def unregister():
    utils.bpy.unregister_classes(CLASSES)
    return None