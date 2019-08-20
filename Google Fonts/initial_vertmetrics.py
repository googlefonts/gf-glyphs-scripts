#MenuTitle: Initial setting of vertical metrics
'''

Calculates vertical metrics according to https://github.com/googlefonts/fontbakery/issues/2164#issuecomment-436595886, sets them in all masters, deletes them in all instances.
Also refer to "The Webfont Strategy, more general" section at https://glyphsapp.com/tutorials/vertical-metrics

'''

from GlyphsApp import *
f = Glyphs.font

import unicodedata

def recursiveDecompositionUnicodes(char):
    '''Recursively lists all unicodes that a given character is composed of, using Python’s own unicodedata module. 
    Example:
        A -> ['0041']
        Ă -> ['0041', '0306']
        Ắ -> ['0041', '0306', '0301']'''

    import unicodedata
    
    unicodes = []
    decompositionList = unicodedata.decomposition(char).split(' ')

    # Catch '<compat>' value    
    try:
        l = [int(x, 16) for x in decompositionList if x]
    except:
        return []

    if decompositionList:
        recursive = []  
        for code in decompositionList:
            if code:
                r = recursiveDecompositionUnicodes(unichr(int(code, 16)))
                recursive.extend(r)
        
        if recursive:
            unicodes.extend(recursive)
        else:
            unicodes.extend([str(hex(ord(char)).split('x')[1].zfill(4))])
    
    return unicodes


def verticalBBox(glyph):
    
    _max = None
    _min = None
    
    for layer in glyph.layers:
        
        top = layer.bounds.origin.y + layer.bounds.size.height
        bottom = layer.bounds.origin.y
        
        if not _max:
            _max = top
        else:
            _max = max(_max, top)
        if not _min:
            _min = bottom
        else:
            _min = min(_min, bottom)

    return _min, _max       
        
            
            
tallestSingleAccentCap = None
lowestLowercase = None
yMax = None
yMin = None

for g in f.glyphs:  

    bbox = verticalBBox(g)
    _min, _max = bbox

    if g.string:

        # tallestSingleAccentCapGlyph
        # Checking the tallest Latin uppercase glyph that has a single accent (decomposition amount = 2)
        if unicodedata.category(g.string) == 'Lu' and len(recursiveDecompositionUnicodes(g.string)) == 2:
            if not tallestSingleAccentCap:
                tallestSingleAccentCap = _max
            else:
                tallestSingleAccentCap = max(tallestSingleAccentCap, _max)

        # tallestSingleAccentCapGlyph
        # Checking the lowest Latin lowercase glyph without any accents (decomposition amount = 1)
        if unicodedata.category(g.string) == 'Ll' and len(recursiveDecompositionUnicodes(g.string)) == 1:
            if not lowestLowercase:
                lowestLowercase = _min
            else:
                lowestLowercase = min(lowestLowercase, _min)
                
    # yMax/yMin
    if _min:
        if not yMin:
            yMin = _min
        else:
            yMin = min(yMin, _min)
    if _max:
        if not yMax:
            yMax = _max
        else:
            yMax = max(yMax, _max)
        
parameters = ['hheaAscender', 'hheaDescender', 'hheaLineGap', 'typoAscender', 'typoDescender', 'typoLineGap', 'winAscent', 'winDescent']

# Set these values for all masters:
for master in f.masters:
    master.customParameters['hheaAscender'] = tallestSingleAccentCap
    master.customParameters['hheaDescender'] = lowestLowercase
    master.customParameters['hheaLineGap'] = 0
    master.customParameters['typoAscender'] = tallestSingleAccentCap
    master.customParameters['typoDescender'] = lowestLowercase
    master.customParameters['typoLineGap'] = 0
    master.customParameters['winAscent'] = yMax
    master.customParameters['winDescent'] = abs(yMin)

# Delete the values from all instances
for instance in f.instances:
    for parameter in parameters:
        del instance.customParameters[parameter]
