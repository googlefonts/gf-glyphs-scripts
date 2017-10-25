#MenuTitle: Fix fonts for GF spec
'''
Fix/add requirements from ProjectChecklist.md
'''
import os
import re
from utils import (
    download_gf_family,
    ttf_family_style_name,
    RepoDoc,
    UPSTREAM_REPO_DOC,
    norm_m,
    convert_camelcase
)
from datetime import datetime
from vertmetrics import shortest_tallest_glyphs
import templates

BAD_PARAMETERS = [
    'openTypeNameLicense',
    'openTypeNameLicenseURL',
    'panose',
    'unicodeRanges',
    'codePageRanges',
    'openTypeNameDescription',
    'Family Alignment Zones',
]

def style_from_ttf(ttf):
    family, style = ttf_family_style_name(ttf)
    return style


def gen_copyright_string(font):
    """Automatically Generate the family's copyright string, using the
    GF Repo doc, http://tinyurl.com/kd9lort"""
    current_copyright = font.copyright
    year = re.search(r'[0-9]{4}', current_copyright)
    if year:
        year = year.group(0)
    else:
        year = datetime.now().year

    project_name = font.familyName
    current_rfn = re.search(r'(?<=Reserved Font Name \").*(?=\")', current_copyright)

    repo_doc = RepoDoc()
    git_url = repo_doc.family_url(font.familyName)
    if not git_url:
        print ('WARNING: Cannot auto gen copyright string. Git url not listed in '
               'Repo Doc, %s. If family was recently added, it may take a while '
               'for the GF sheet API to update it.') % UPSTREAM_REPO_DOC
        return

    if not current_rfn:
        new_copyright = 'Copyright %s The %s Project Authors (%s)' % (
            year,
            project_name,
            git_url
        )
    else:
        new_copyright = ('Copyright %s The %s Project Authors (%s), '
                         'with Reserved Font Name "(%s)".') % (
            year,
            project_name,
            git_url,
            current_rfn.group(0)
        )
    font.copyright = new_copyright


def gen_ofl(copyright_string):

    ofl_text = templates.ofl_text.replace('{{ copyright_string }}', copyright_string)
    ofl_path = os.path.join(project_dir, 'OFL.txt')
    with open(ofl_path, 'w') as ofl_doc:
        ofl_doc.write(ofl_text)


def visual_inherit_vertical_metrics(font, ttfs_gf):
    """Inherit vertical metrics from family hosted on GF.

    Approach will ensure metrics look the same as the previous release and
    across all platforms, whilst avoiding clipping in MS applications."""
    masters = font.masters
    # ExtraBold Italic - ExtraBoldItalic
    masters_h = {str(m.name.replace(' ', '')): m for m in masters}

    ttfs_gf_h = {style_from_ttf(f): f for f in ttfs_gf}

    # Masters which match downloaded ttf
    mm_styles = set(masters_h.keys()) & set(ttfs_gf_h.keys())
    for style in mm_styles:
        master = masters_h[style]
        ttf_gf = ttfs_gf_h[style]

        # Is Use Typo Metrics enabled?
        master_use_typo_metrics = master.customParameters['Use Typo Metrics'] \
            if master.customParameters['Use Typo Metrics'] \
            else font.customParameters['Use Typo Metrics']
        ttf_gf_use_typo_metrics = ttf_gf['OS/2'].fsSelection & 0b10000000

        # Get upms
        master_upm = master.customParameters['Scale to UPM'] \
            if master.customParameters['Scale to UPM']\
            else font.upm
        ttf_gf_upm = ttf_gf['head'].unitsPerEm

        if master_use_typo_metrics and ttf_gf_use_typo_metrics:

            master.customParameters['typoAscender'] = norm_m(ttf_gf['OS/2'].sTypoAscender, ttf_gf_upm, master_upm)
            master.customParameters['typoDescender'] = norm_m(ttf_gf['OS/2'].sTypoDescender, ttf_gf_upm, master_upm)
            master.customParameters['typoLineGap'] = norm_m(ttf_gf['OS/2'].sTypoLineGap, ttf_gf_upm, master_upm)

        elif master_use_typo_metrics and not ttf_gf_use_typo_metrics:
            master.customParameters['typoAscender'] = norm_m(ttf_gf['OS/2'].usWinAscent, ttf_gf_upm, master_upm)
            master.customParameters['typoDescender'] = norm_m(ttf_gf['OS/2'].usWinDescent, ttf_gf_upm, master_upm)
            master.customParameters['typoLineGap'] = 0

        master.customParameters['hheaAscender'] = norm_m(ttf_gf['hhea'].ascent, ttf_gf_upm, master_upm)
        master.customParameters['hheaDescender'] = norm_m(ttf_gf['hhea'].descent, ttf_gf_upm, master_upm)
        master.customParameters['hheaLineGap'] = norm_m(ttf_gf['hhea'].lineGap, ttf_gf_upm, master_upm)


def set_win_asc_win_desc_to_bbox(font):
    masters = font.masters
    ymin, ymax = shortest_tallest_glyphs(font)
    for master in masters:
        master.customParameters['winDescent'] = abs(ymin)
        master.customParameters['winAscent'] = ymax


def main():
    # Add README file if it does not exist

    font = Glyphs.font
    gen_copyright_string(font)
    font.customParameters['license'] = 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL'
    font.customParameters['licenseURL'] = 'http://scripts.sil.org/OFL'
    font.customParameters['fsType'] = []
    font.customParameters['Use Typo Metrics'] = True
    font.customParameters['Disable Last Change'] = True
    font.customParameters['Use Line Breaks'] = True

    # Delete unnecessary customParameters
    for key in BAD_PARAMETERS:
        del font.customParameters[key]

    # Add http:// to manufacturerURL and designerURL if they don't exist
    if font.manufacturerURL:
        if not font.manufacturerURL.startswith(('http://', 'https://')):
            font.manufacturerURL = 'http://' + font.manufacturerURL
    else:
        print 'WARNING: manufacturerURL is missing'

    if font.designerURL:
        if not font.designerURL.startswith(('http://', 'https://')):
            font.designerURL = 'http://' + font.designerURL
    else:
        print 'WARNING: designerURL is missing'

    # Remove glyph order
    if 'glyphOrder' in font.customParameters:
        del font.customParameters['glyphOrder']

    masters = font.masters
    instances = font.instances

    # if uni00A0 rename it
    if font.glyphs['uni00A0']:
        font.glyphs['uni00A0'].name = 'nbspace'

    # If nbspace does not exist, create it
    if not font.glyphs['nbspace']:
        nbspace = GSGlyph()
        nbspace.name = 'nbspace'
        nbspace.unicode = unicode('00A0')
        font.glyphs.append(nbspace)

    # if uni000D rename it
    if font.glyphs['uni000D']:
        font.glyphs['uni000D'].name = 'CR'

    # If CR does not exist, create it
    if not font.glyphs['CR']:
        cr = GSGlyph()
        cr.name = 'CR'
        font.glyphs.append(cr)

    # if .null rename it
    if font.glyphs['.null']:
        font.glyphs['.null'].name = 'NULL'

    # If NULL does not exist, create it
    if not font.glyphs['NULL']:
        null = GSGlyph()
        null.name = 'NULL'
        font.glyphs.append(null)

    font.glyphs['CR'].unicode = unicode('000D')
    font.glyphs['NULL'].unicode = unicode('0000')

    # fix width glyphs
    for i, master in enumerate(masters):
        # Set nbspace width so it matches space
        font.glyphs['nbspace'].layers[i].width = font.glyphs['space'].layers[i].width
        # Set NULL width so it is 0
        font.glyphs['NULL'].layers[i].width = 0
        # Set CR so width matches space
        font.glyphs['CR'].layers[i].width = font.glyphs['space'].layers[i].width

    # fix instance names to pass gf spec
    for i, instance in enumerate(instances):
        if 'Oblique' in instance.name:
            instance.name = instance.name.replace('Oblique', 'Italic')
        if 'Italic' in instance.name:
            instance.isItalic = True
            instance.name = instance.weight + ' Italic'
            if instance.weight != 'Bold' and instance.weight != 'Regular':
                instance.linkStyle = instance.weight
            else:
                instance.linkStyle = ''
        else:
            instance.name = instance.weight
            instance.linkStyle = ''

        # Seperate non Reg/Medium widths into their own family
        if instance.width != 'Medium (normal)':
            if instance.width == 'Semi Expanded':
                family_suffix = instance.width
            else:
                family_suffix = convert_camelcase(instance.width)
            sub_family_name = '%s %s' % (font.familyName, family_suffix)
            instance.customParameters['familyName'] = sub_family_name
            if 'Italic' in instance.name:
                instance.name = instance.weight + ' Italic'
            else:
                instance.name = instance.weight

        if instance.weight == 'Bold':
            instance.isBold = True
        else:
            instance.isBold = False

        # Change ExtraLight weight class from 250 to 275
        if instance.weight == 'ExtraLight':
            instance.customParameters['weightClass'] = 275

        # If Heavy exists, create a new font family for it
        if 'Heavy' in instance.name:
            instance.customParameters['familyName'] = '%s Heavy' % (font.familyName)
            instance.name = instance.name.replace('Heavy', 'Regular')
            instance.weight = 'Regular'

        if instance.name == 'Regular Italic':
            instance.name = 'Italic'

    # Regressions fixing
    ttfs_gf = download_gf_family(font.familyName)
    if ttfs_gf:
        visual_inherit_vertical_metrics(font, ttfs_gf)
    set_win_asc_win_desc_to_bbox(font)

    # txt file generation
    gen_ofl(font.copyright)


if __name__ == '__main__':
    Glyphs.showMacroWindow()
    __glyphsfile = Glyphs.font.filepath
    project_dir = os.path.abspath(
        os.path.join(os.path.dirname(__glyphsfile), '..')
    )
    main()
    print 'Fonts updated to GF spec'

