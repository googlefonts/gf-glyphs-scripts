#MenuTitle: Proof kerning for current master


def _glyph_ids_to_glyph_names(font):
	results = {}
	for glyph in font.glyphs:
		results[glyph.id] = glyph.name
	return results


def pad_glyph(font, glyph_name):
	try:
		pad_type = font.glyphs[glyph_name].subCategory
		if pad_type == "Uppercase":
			pad = "H"
		else:
			pad = "n"
	except AttributeError:
		pad = "n"
	return "{}/{}".format(pad, pad)


def get_kern_strings(font):
	kern_strings = []
	
	ids_to_names = _glyph_ids_to_glyph_names(font)
        master = font.selectedFontMaster.id
	for left_key in font.kerning[master]:
		for right_key in font.kerning[master][left_key]:
			left = left_key.split('_')[-1] if '_' in left_key \
			        else ids_to_names[left_key]
			right = right_key.split('_')[-1] if '_' in right_key \
			        else ids_to_names[right_key]
			
			pad_left = pad_glyph(font, left)
			pad_right = pad_glyph(font, right)
			kern_strings.append("/{}/{}/{}/{}".format(pad_left, left, right, pad_right))
	return '\n'.join(kern_strings)


def main():
	font = Glyphs.font
	kern_strings = get_kern_strings(font)
	font.newTab(kern_strings)


if __name__ == '__main__':
	main()

