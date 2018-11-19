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
	conflictingComponents = []

	for i in range(len(actualComponents) - 1):
		for anchor in font.glyphs[components[i]].layers[0].anchors:
			baseAnchors.update({anchor.name : components[i]})
				
		for anchor in font.glyphs[components[i + 1]].layers[0].anchors:
			if re.match('^_.*', anchor.name) != None:
				attachAnchors.update({anchor.name : components[i + 1]})

	# for i in range(len(actualComponents)):
	# 	for anchor in font.glyphs[components[i]].layers[0].anchors:
	# 		if re.match('^_.*', anchor.name) == None:
	# 			baseAnchors.update({anchor.name : components[i]})
	# 		else:
	# 			attachAnchors.update({anchor.name : components[i]})
				
	counts = {}
	for component in components:
		counts.update({component : 0})
		
	for item in attachAnchors.keys():
		if baseAnchors.get(re.sub('^_', '', item)) != None:
			counts.update({attachAnchors[item] : counts[attachAnchors[item]] + 1})
			conflictingAnchors.append(str(re.sub('^_', '', item)))
			conflictingComponents.append(attachAnchors[item])
		else:
			pass
	
	for count in counts.keys():
		if counts[count] > 1:
			glyphNames = glyphNames + "/" + glyph.name
			print "%s has %d conflicting anchors:" % (glyph.name, counts[count])
			for i in range(len(conflictingAnchors)):
				print "%s in %s" % (conflictingAnchors[i], conflictingComponents[i])
			print "\n"
	
	return glyphNames
				
	
glyphNames = ""
for glyph in font.glyphs:
	actualComponents = [component.name for component in glyph.layers[0].components]
	glyphNames = checkActualComponents(actualComponents, glyph, glyphNames)
	font.tabs[-1].text = glyphNames