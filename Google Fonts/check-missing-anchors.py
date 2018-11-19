#MenuTitle: Check Missing Anchors
# -*- coding: utf-8 -*-
"""
Checks if there are any mismatched anchors across masters relative to the first master. Opens the problematic layers in a new tab
"""

font = Glyphs.font


font.newTab().layers = []

for glyph in font.glyphs:
	baseAnchors = {}
	for layer in glyph.layers:
		addLayer = False
		if layer.layerId == layer.parent.layers[0].layerId:
			for anchor in layer.anchors:
					baseAnchors.update({anchor.name : anchor.name})
		else:
			layerAnchors = {}
			for anchor in layer.anchors:
				layerAnchors.update({anchor.name : anchor.name})
				if baseAnchors.get(anchor.name, None) == None:
					addLayer = True
					print "%s has extra anchor \'%s\' on %s layer" % (glyph.name, anchor.name, layer.name)
			for anchorName in baseAnchors.keys():
				if layerAnchors.get(anchorName, None) == None:
					addLayer = True
					print "%s is missing anchor \'%s\' on %s layer" % (glyph.name, anchorName, layer.name)
				
				
					
		if addLayer == True:
			font.tabs[-1].layers.append(layer)