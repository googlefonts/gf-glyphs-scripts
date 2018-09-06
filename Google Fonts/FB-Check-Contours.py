#MenuTitle: FB Check Contours
# -*- coding: utf-8 -*-
"""
Runs a modified version of check 153 from FontBakery within Glyphs App and opens a new tab with the layers that deviate from the expected number of contours
(Works non-destructively so all components are retained)
"""

from glyphdata import desired_glyph_data
import re

font = Glyphs.font

font.newTab().layers = []

def checkCounters(glyph, contours):
	for layer in glyph.layers:
		if layer.layerId == layer.associatedMasterId or re.match("\[\d*[\[, \]]", layer.name) != None or re.match("\{\d*[\{, \}]", layer.name) != None:
			tempLayer = layer.copyDecomposedLayer()
			tempLayer.removeOverlap()
			count = len(tempLayer.paths)
		
			if count in contours:
				pass
			else:
				font.tabs[-1].layers.append(layer)
				print glyph.name, "Expected Contours: %s" % str(contours), "Current Contours: %d" % count
	

for data in desired_glyph_data:
	if font.glyphs[data["name"]] != None and font.glyphs[data["name"]].export == True:
		checkCounters(font.glyphs[data["name"]], data["contours"])
	elif font.glyphs[Glyphs.glyphInfoForUnicode(data["unicode"]).name] != None and font.glyphs[Glyphs.glyphInfoForUnicode(data["unicode"]).name].export == True:
		checkCounters(font.glyphs[Glyphs.glyphInfoForUnicode(data["unicode"]).name], data["contours"])
	else:
		pass
		
	
Glyphs.showMacroWindow()
