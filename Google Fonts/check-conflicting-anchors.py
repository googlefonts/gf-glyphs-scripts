#MenuTitle: Check Conflicting Anchors
# -*- coding: utf-8 -*-
"""
Checks all glyphs to see if composites have multiple attachment points for one component(i.e. conflicting anchors), and opens these glyphs in a new tab
"""
import re

font = Glyphs.font

font.newTab().text = ""

def checkActualComponents(components ,glyph, glyphNames):
	baseAnchors = {}
	attachAnchors = {}
	conflictingAnchors = []
	for i in range(len(actualComponents) - 1):
		for anchor in font.glyphs[components[i]].layers[0].anchors:
			if re.match('^_.*', anchor.name) == None:
				baseAnchors.update({anchor.name : components[i]})
				
		for anchor in font.glyphs[components[i + 1]].layers[0].anchors:
			if re.match('^_.*', anchor.name) != None:
				attachAnchors.update({anchor.name : components[i + 1]})
				
	count = 0
	for item in attachAnchors.keys():
		if baseAnchors.get(re.sub('^_', '', item)) != None:
			count = count + 1
			conflictingAnchors.append(str(re.sub('^_', '', item)))
			addGlyph = True
		else:
			pass
	
	if count > 1:
		glyphNames = glyphNames + "/" + glyph.name
		print "%s has %d conflicting anchors:" % (glyph.name, count)
		print "%s" % re.sub('\[', '', re.sub('\]', '', str(conflictingAnchors)))
		print "\n"
	
	return glyphNames
				
	
glyphNames = ""
for glyph in font.glyphs:
	actualComponents = [component.name for component in glyph.layers[0].components]
	glyphNames = checkActualComponents(actualComponents, glyph, glyphNames)
	font.tabs[-1].text = glyphNames