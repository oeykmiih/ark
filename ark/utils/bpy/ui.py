# SPDX-License-Identifier: GPL-2.0-or-later
import bpy

from . import ops

def label(layout, text="", depress=False, align=True):
    widget = layout.row(align=align)
    widget.operator(
        ops.UTILS_OT_Placeholder.bl_idname,
        text=text,
        depress=depress,
    )
    return widget

def alert(layout, text="", align=True):
    widget = layout.column(align=align)
    widget.alert = True
    widget.operator(
        ops.UTILS_OT_Placeholder.bl_idname,
        text=text,
    )
    return widget

def split(layout, text="", align=True, enabled=True):
    row = layout.row(align=True).split(factor=0.4, align=True)
    row.enabled = enabled
    label = row.row()
    label.alignment = 'RIGHT'
    label.label(text=text)

    sub = row.row(align=True)
    return sub