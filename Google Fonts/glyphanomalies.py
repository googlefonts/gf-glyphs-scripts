#MenuTitle: Report glyph anomalies
from copy import deepcopy


def glyph_nodes(layer):
	res = []
	for path in layer.paths:
		for node in path.nodes:
			res.append((node.x, node.y))
	return res


def node_distances(glyph_nodes):
	glyph_distances = [0] * len(glyph_nodes)
	for idx, (x1,y1) in enumerate(glyph_nodes):
		for x2, y2 in glyph_nodes:
			dist = ((abs(x1-x2)**2) + (abs(y1-y2)**2)) ** 0.5 
			glyph_distances[idx] += dist
	return glyph_distances

	
def normalize(float_list):
    if not float_list:  # Check if the list is empty
        return []

    min_val = min(float_list)
    max_val = max(float_list)
    range_val = max_val - min_val

    if range_val == 0:  # Avoid division by zero if all elements are the same
        return [0.0] * len(float_list)

    # Normalize the list
    normalized_list = [(x - min_val) / range_val for x in float_list]
    return normalized_list


def normalize_glyph(glyph):
	res = []
	for layer in glyph.layers:
		nodes = glyph_nodes(layer)
		distances = node_distances(nodes)
		norm = normalize(distances)
		scaled = scaler(layer, norm)
		res.append(norm)
	return res

def scaler(layer, norm):
	res = []
	scale = 0
	for axis in layer.master.axes:
		scale += axis / 1000
	
	for val in norm:
		res.append(val * scale)
	return res

	
def anomoly_score(res):
	r = -float("inf")
	for i in range(1, len(res)):
		curr = res[i]
		prev = res[i-1]
		try:
			for j in range(len(curr)):
				val = abs(curr[j]-prev[j])
				r = max(r, val)
		except:
			r = float("inf")
	return r


def prepare_font(font):
	# sort masters by axis vals
	font.masters = sorted([m for m in font.masters], key=lambda k: sum(k.axes))
	# decompose comps
	for glyph in font.glyphs:
		for layer in glyph.layers:
			layer.decomposeComponents()


def main():
	threshold = 0.2
	results = set()
	original_font = Glyphs.font
	font = deepcopy(Glyphs.font)
	
	prepare_font(font)

	for glyph in font.glyphs:
		n = normalize_glyph(glyph)
		score = anomoly_score(n)
		if score > threshold:
			results.add((glyph.name, score))
	
	results = sorted(results, key=lambda k: k[1], reverse=True)
	for name, score in results:
		print(name, score)
	print("Please be aware there may be some false positives!")
	string_list = "/\n/".join([n for n,_ in results])
	original_font.newTab("/" + string_list + "/")
	

if __name__ == "__main__":
	main()