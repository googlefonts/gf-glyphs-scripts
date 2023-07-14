#MenuTitle: Fix starting points
# -*- coding: utf-8 -*-
"""
Fix starting points in masters. Paths must been in correct order
and contain the same number of nodes as the first master.

Fixes issues such as:
https://github.com/SorkinType/Merriweather/issues/540
"""

def fix_starting_points(base, to_match_m):
	dflt = [(n.x, n.y) for n in base.nodes]
	to_match = [(n.x, n.y) for n in to_match_m.nodes]
	
	best_score = float('inf')
	best = 0
	for i in range(len(to_match)+1):
		res = to_match[i:] + to_match[:i]
		score = sum([abs(a_x - b_x) + abs(a_y - b_y) for (a_x, a_y),(b_x, b_y) in zip(dflt, res)])
		base_type = base.nodes[-1].type
		res_type = to_match_m.nodes[i-1].type
		if base_type == res_type and score < best_score:
			best_score = score
			best = i-1
	to_match_m.nodes[best].makeNodeFirst()


font = Glyphs.font
for glyph in font.glyphs:
	base_master = glyph.layers[0]
	for layer in glyph.layers[1:]:
		for base_path, to_match in zip(base_master.paths, layer.paths):
			fix_starting_points(base_path, to_match)

print("Done")