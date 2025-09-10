#MenuTitle: Move Selected Nodes Along Normal (with Offset Prompt)
# -*- coding: utf-8 -*-
__doc__="""
Prompts for an offset and moves selected nodes of the active layer along their local path normals.
"""

import math
from vanilla import FloatingWindow, EditText, TextBox, Button

class OffsetDialog(object):
    def __init__(self):
        self.w = FloatingWindow((220, 80), "Move Along Normal")
        self.w.text = TextBox((10, 12, -10, 20), "Offset amount:")
        self.w.input = EditText((100, 10, -10, 22), "20")
        self.w.button = Button((10, 40, -10, 22), "Apply", callback=self.apply)
        self.w.open()
        self.w.makeKey()

    def apply(self, sender):
        try:
            offset = float(self.w.input.get())
        except ValueError:
            offset = 0
        moveSelectedNodes(offset)
        self.w.close()

def normal_at_node(path, nodeIndex):
    prevNode = path.nodes[nodeIndex - 1]
    currNode = path.nodes[nodeIndex]
    nextNode = path.nodes[(nodeIndex + 1) % len(path.nodes)]

    dx = nextNode.x - prevNode.x
    dy = nextNode.y - prevNode.y
    length = math.hypot(dx, dy)
    if length == 0:
        return (0, 0)

    tx = dx / length
    ty = dy / length
    nx = -ty
    ny = tx
    return (nx, ny)

def moveSelectedNodes(offset):
    font = Glyphs.font
    layer = font.selectedLayers[0]

    for path in layer.paths:
        for i, node in enumerate(path.nodes):
            if node.selected:
                nx, ny = normal_at_node(path, i)
                node.x += nx * offset
                node.y += ny * offset

    layer.applyTransform([1, 0, 0, 1, 0, 0])  # refresh

OffsetDialog()
