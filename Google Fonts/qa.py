#MenuTitle: QA
# -*- coding: utf-8 -*-
"""
Check GF upstream repositories pass GF checklist,
https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md
"""
import unittest
from unittest import TestProgram
from runner import GlyphsTestRunner
import os
from ntpath import basename
from fontTools.ttLib import TTFont
import csv
from StringIO import StringIO
from zipfile import ZipFile
import re
from datetime import datetime
import shutil
import tempfile
from math import ceil

from vertmetrics import VERT_KEYS, shortest_tallest_glyphs
from utils import *

FONT_ATTRIBS = [
    'familyName',
    'upm',
    'designer',
    'designerURL',
    'copyright',
    'manufacturer',
    'manufacturerURL',
    'versionMajor',
    'versionMinor',
    'date',
]

LICENSE = '%s%s%s' % (
    'This Font Software is licensed under the SIL Open Font License, ',
    'Version 1.1. This license is available with a FAQ at: ',
    'http://scripts.sil.org/OFL'
)

LICENSE_URL = 'http://scripts.sil.org/OFL'

SOURCES_FOLDER = 'sources'
FONTS_FOLDER = 'fonts'


STYLE_NAMES = [
    'Thin',
    'ExtraLight',
    'Light',
    'Regular',
    'Medium',
    'SemiBold',
    'Bold',
    'ExtraBold',
    'Black',
    'Thin',
    'ExtraLight',
    'Light',
    'Regular',
    'Medium',
    'SemiBold',
    'Bold',
    'ExtraBold',
    'Black',
    'Thin Italic',
    'ExtraLight Italic',
    'Light Italic',
    'Italic',
    'Medium Italic',
    'SemiBold Italic',
    'Bold Italic',
    'ExtraBold Italic',
    'Black Italic',
    'Thin Italic',
    'ExtraLight Italic',
    'Light Italic',
    'Regular Italic',
    'Medium Italic',
    'SemiBold Italic',
    'Bold Italic',
    'ExtraBold Italic',
    'Black Italic',
]

STYLE_WEIGHTS = {
    'Thin': 250,
    'ExtraLight': 275,
    'Light': 300,
    'Regular': 400,
    'Medium': 500,
    'SemiBold': 600,
    'Bold': 700,
    'ExtraBold': 800,
    'Black': 900,
    'Thin Italic': 250,
    'ExtraLight Italic': 275,
    'Light Italic': 300,
    'Italic': 400,
    'Medium Italic': 500,
    'SemiBold Italic': 600,
    'Bold Italic': 700,
    'ExtraBold Italic': 800,
    'Black Italic': 900,
}


class TestGlyphsFiles(unittest.TestCase):
    """Class loads/generates necessary files for unit tests."""
    @classmethod
    def setUpClass(cls):
        cls.fonts = Glyphs.fonts

        cls._repos_doc = None
        cls._remote_font = None
        cls._ttfs = None
        cls._temp_dir = tempfile.mkdtemp()
        cls._repo_doc = None

    @classmethod
    def tearDownClass(cls):
        """Remove the temporarily generated folder and its files"""
        shutil.rmtree(cls._temp_dir)

    @property
    def remote_font(self):
        """If the family already exists on Google Fonts, download and
        parse the ttfs into a GSFont object, else return None"""
        if not self._remote_font:
            return download_gf_family(self.fonts[0].familyName)
        return None

    @property
    def repo_doc(self):
        """Return a csv DictReader object of the GF_Repo doc"""
        if not self._repos_doc:
            self._repos_doc = RepoDoc()
        return self._repos_doc

    @property
    def ttfs(self):
        """Return the generated .ttfs from the open .glyphs files"""
        if not self._ttfs:
            for font in self.fonts:
                for instance in font.instances:
                    instance.generate(Format='ttf', FontPath=self._temp_dir)
        self._ttfs = [TTFont(os.path.join(self._temp_dir, f)) for f
                      in os.listdir(self._temp_dir) if f.endswith('.ttf')]
        return self._ttfs


class TestFontInfo(TestGlyphsFiles):

    def test_copyright(self):
        """Check copyright string is correct

        https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md#ofltxt

        The string must include the git repo url.
        """
        
        repo_git_url = None
        for font in self.fonts:
            if not repo_git_url:
                repo_git_url = self.repo_doc.family_url(font.familyName)

            family_copyright_pattern = r'Copyright [0-9]{4} The %s Project Authors \(%s\)' % (
                font.familyName, repo_git_url
            )

            copyright_search = re.search(family_copyright_pattern, font.copyright)
            
            self.assertIsNotNone(
                repo_git_url,
                ('Copyright does not contain git url.\n\n'
                 'GF Upstream doc has no git url for family. '
                 'If the family has been recently added, it may take 5 minutes '
                 'for the Google Sheet API to update it.'
                )
            )

            self.assertIsNotNone(
                copyright_search,
                ('Copyright string is incorrect.\n\n'
                 'It must contain or be:\n'
                 'Copyright %s The %s Project Authors (%s)\n\n'
                 'If the family has a RFN:\n'
                 'Copyright %s The %s Project Authors (%s), '
                 'with Reserved Font Name "%s".') % (
                    datetime.now().year,
                    font.familyName,
                    repo_git_url,
                    datetime.now().year,
                    font.familyName,
                    repo_git_url,
                    font.familyName,
                )
            )

    def test_style_names(self):
        """Check instances have the correct name for the GF API"""
        for font in self.fonts:
            instances = font.instances
            family_styles = set([i.name for i in instances])
            for style in family_styles:
                self.assertIn(
                    style,
                    STYLE_NAMES,
                    ("'%s' instance is an invalid name.\n\n"
                     "The following names are accepted:\n- "
                     "%s") % (style, '\n- '.join(STYLE_NAMES)))

    def test_license_url(self):
        """Check family has 'licenseURL' custom parameter"""
        for font in self.fonts:
            self.assertEqual(
                font.customParameters['licenseURL'],
                LICENSE_URL,
                ("License url is incorrect.\n\n"
                 "font.customParameters['licenseURL'] must be '%s'") % LICENSE_URL
            )

    def test_license(self):
        """Check family has 'license' custom parameter"""
        for font in self.fonts:
            self.assertEqual(
                font.customParameters['license'],
                LICENSE,
                ("License is incorrect.\n\n"
                 "font.customParameters['license'] must be '%s'") % LICENSE
            )

    def test_instance_weight_class(self):
        """Check each instance has the correct weight value"""
        for font in self.fonts:
            instances = font.instances
            for instance in instances:
                try:
                    self.assertEqual(
                        instance.weightClassValue(),
                        STYLE_WEIGHTS[instance.name],
                        ("%s instance weight value is incorrect.\n\n"
                         "It must be set to '%s'.") % (
                            instance.name,
                            STYLE_WEIGHTS[instance.name]
                        )
                    )
                except KeyError:
                    print '%s is not a correct style name' % instance.name

    def test_single_instance_family_is_regular(self):
        """Check single weight families have Regular style name

        If the font only has one instance, make sure its stylename and
        weight value is set to Regular, 400.

        Some MS application struggle when a family does not include a
        Regular weight.

        Single weight families which visually look heavy are not exempt
        from this rule."""
        for font in self.fonts:
            instances = font.instances
            if len(instances) == 1 and self.fonts < 2:
                instance = instances[0]
                self.assertEqual(
                    instance.name,
                    'Regular',
                    ("'%s' instance name is incorrect.\n\n"
                     "Families which have just one instance must "
                     "name the single 'Regular'") % instance.name
                )

    def test_italic_instances_have_isItalic_set(self):
        """Check only italic instances have 'isItalic' set"""
        for font in self.fonts:
            instances = font.instances
            for instance in instances:
                if 'Italic' in instance.name:
                    self.assertEqual(
                        instance.isItalic,
                        True,
                        "'%s' instance is an Italic.\n\n"
                        "Enable 'Italic of' for the instance" % (
                            instance.name
                        )
                    )
                else:
                    self.assertEqual(
                        instance.isItalic,
                        False,
                        "'%s' instance is not an Italic.\n\n"
                        "Disable 'Italic of' for the instance" % (
                            instance.name
                        )
                    )

    def test_instances_have_isBold_set(self):
        """Check only Bold and Bold Italic have 'isBold' set"""
        for font in self.fonts:
            instances = font.instances
            for instance in instances:
                if instance.name == 'Bold' or instance.name == 'Bold Italic':
                    self.assertEqual(
                        instance.isBold,
                        True,
                        "'%s' instance is a Bold weight.\n\n"
                        'Enable "Bold of" for this instance.' % (
                            instance.name
                        )
                    )
                else:
                    self.assertEqual(
                        instance.isBold,
                        False,
                        "'%s' instance is not a Bold weight.\n\n"
                        'Disable "Bold of" for this instance.\n\n'
                        "Only the 'Bold' and 'Bold Italic instances "
                        "should have this flag enabled" % (
                            instance.name
                        )
                    )

    def test_stylelinking_is_consistent_for_all_italic_instances(self):
        """Check style linking is correct for italic instances"""
        for font in self.fonts:
            instances = font.instances
            for instance in instances:
                if 'Italic' in instance.name:
                    if instance.name == 'Italic' or instance.name == 'Bold Italic':
                        self.assertEqual(
                            '',
                            instance.linkStyle,
                            ("%s instance must have no style linking.\n\n"
                             "Delete link to %s") % (
                                instance.name,
                                instance.linkStyle
                            )
                        )
                    else:
                        roman_link_style = instance.name.split()[0]
                        self.assertEqual(
                            roman_link_style,
                            instance.linkStyle,
                            "%s instance must be style linked to %s" % (
                                instance.name,
                                roman_link_style
                            )
                        )

    def test_stylelinking_is_consistent_for_all_non_italic_instances(self):
        """Check style linking is correct for non italic instances"""
        for font in self.fonts:
            instances = font.instances
            for instance in instances:
                if 'Italic' not in instance.name:
                    self.assertEqual(
                        '',
                        instance.linkStyle,
                        ("%s instance must have no style linking."
                         " Delete link to %s") % (
                            instance.name,
                            instance.linkStyle 
                        )
                    )


class TestMultipleGlyphsFileConsistency(unittest.TestCase):
    """Families are often split into multiple .glyphs files.

    Make sure certain attributes share the same values"""
    def setUp(self):
        self.fonts = Glyphs.fonts

    def test_files_share_same_attributes(self):
        """Check all .glyph files share same parameters"""
        for font1 in self.fonts:
            for font2 in self.fonts:
                for attrib in FONT_ATTRIBS:
                    self.assertEqual(
                        getattr(font1, attrib),
                        getattr(font2, attrib),
                        ("Files do not have equal attribute parameters.\n\n"
                         "%s %s: %s\n%s %s: %s") % (
                            basename(font1.filepath),
                            attrib,
                            getattr(font1, attrib),
                            basename(font2.filepath),
                            attrib,
                            getattr(font2, attrib)
                        )
                    )

    def test_font_customParameters_are_equal(self):
        """Check all .glyph files share same custom parameters"""
        for font1 in self.fonts:
            for font2 in self.fonts:
                for param in font1.customParameters:
                    self.assertEqual(
                        font1.customParameters[param.name],
                        font2.customParameters[param.name],
                        ("Files do not have equal custom parameters.\n\n"
                         "%s %s: %s\n%s %s: %s") % (
                            basename(font1.filepath),
                            param.name,
                            font1.customParameters[param.name],
                            basename(font2.filepath),
                            param.name,
                            font2.customParameters[param.name],
                        )
                    )


class TestRegressions(TestGlyphsFiles):
    """If the family already exists on fonts.google.com, download and compare
    the data against the generated .ttf instances from the .glyphs file."""
    def _get_font_styles(self, fonts):
        """Get the Win style name for each font"""
        styles = []
        for font in fonts:
            name = font['name'].getName(2, 3, 1, 1033)
            enc = name.getEncoding()
            styles.append(str(name).decode(enc))
        return set(styles)

    def _hash_fonts(self, ttfs):
        styles = self._get_font_styles(ttfs)
        return dict(zip(styles, ttfs))


    def test_missing_encoded_glyphs(self):
        """Check family includes all encoded glyphs which are in the GF version"""
        if self.remote_font:
            local_fonts = self._hash_fonts(self.ttfs)
            remote_fonts = self._hash_fonts(self.remote_font)
            shared_styles = set(local_fonts.keys()) & set(remote_fonts.keys())

            for style in shared_styles:
                local_cmap = local_fonts[style]['cmap'].getcmap(3, 1).cmap
                remote_cmap = remote_fonts[style]['cmap'].getcmap(3, 1).cmap

                missing_codepoints = set(remote_cmap.keys()) - set(local_cmap.keys())
                missing_glyphs = set([remote_cmap[m] for m in missing_codepoints])
                self.assertEqual(
                    missing_glyphs,
                    set([]),
                    '%s is missing [%s]' % (
                        style,
                        ', '.join(missing_glyphs)
                    )
                )

    def test_missing_instances(self):
        """Check family includes the same styles as GF version"""
        if self.remote_font:
            local_styles = self._get_font_styles(self.ttfs)
            remote_styles = self._get_font_styles(self.remote_font)
            missing = remote_styles - local_styles
            self.assertEqual(missing, set([]),
                            ('Font is missing instances [%s] are all '
                             '.glyphs file open?') % ', '.join(missing))

    def test_version_number_has_advanced(self):
        """Check family version number is greater than GF version

        If the family has a version number lower than the family being
        served on fonts.google.com, it may mean the repository is based on
        older sources. Authors need to investigate if they are working from
        the correct source.

        If the version number is the same and changes have occured, the
        version number needs bumping"""
        if self.remote_font:
            local_version = max([f['head'].fontRevision for f in self.ttfs])
            remote_version = max([f['head'].fontRevision for f in self.remote_font])
            self.assertGreater(
                local_version,
                remote_version,
                "Font Version, %s is not greater than previous release, %s" % (
                        local_version, remote_version
                    )
                )

    def test_vert_metrics_visually_match(self):
        """Test vertical metrics visually match GF version

        Vertical metrics must visually match the version hosted
        on fonts.google.com.

        If the hosted family doesn't have the fsSelection bit 7 enabled,
        we can use this to our advantage. By setting this bit, the typo
        metrics are used instead of the win metrics. This allows us to
        add taller scripts, without affecting the line leading. The win
        metrics can then be set freely. This scenario is common when 
        upgrading legacy families.

        If both the hosted family and the local family have fsSelection
        bit 7 enabled, the typo and hhea values must be the same. The win
        values can be changed freely to accomodate the families bbox ymin
        and ymax values to avoid clipping."""
        if self.remote_font:
            local_fonts = self._hash_fonts(self.ttfs)
            remote_fonts = self._hash_fonts(self.remote_font)
            shared_styles = set(local_fonts.keys()) & set(remote_fonts.keys())

            for style in shared_styles:
                l_font = local_fonts[style]
                r_font = remote_fonts[style]

                # Check if Use Typo metrics bit 7 is enabled
                # https://www.microsoft.com/typography/OTSpec/os2.htm#fss
                l_use_typo_metrics = l_font['OS/2'].fsSelection & 0b10000000
                r_use_typo_metrics = r_font['OS/2'].fsSelection & 0b10000000

                l_upm = l_font['head'].unitsPerEm
                r_upm = r_font['head'].unitsPerEm

                if r_use_typo_metrics and l_use_typo_metrics:
                    self.assertEqual(
                        l_font['OS/2'].sTypoAscender, 
                        norm_m(r_font['OS/2'].sTypoAscender, r_upm, l_upm),
                        "Local %s typoAscender %s is not equal to remote %s typoAscender %s" % (
                            style,
                            l_font['OS/2'].sTypoAscender,
                            norm_m(r_font['OS/2'].sTypoAscender, r_upm, l_upm),
                        )
                    )
                    self.assertEqual(
                        l_font['OS/2'].sTypoDescender, 
                        norm_m(r_font['OS/2'].sTypoDescender, r_upm, l_upm),
                        "Local %s typoDescender %s is not equal to remote %s typoDescender %s" % (
                            style,
                            l_font['OS/2'].sTypoDescender,
                            norm_m(r_font['OS/2'].sTypoDescender, r_upm, l_upm),
                        )
                    )
                    self.assertEqual(
                        l_font['OS/2'].sTypoLineGap, 
                        norm_m(r_font['OS/2'].sTypoLineGap, r_upm, l_upm),
                        "Local %s typoLineGap %s is not equal to remote %s typoLineGap %s" % (
                            style,
                            l_font['OS/2'].sTypoLineGap,
                            style,
                            norm_m(r_font['OS/2'].sTypoLineGap, r_upm, l_upm),
                        )
                    )
                elif l_use_typo_metrics and not r_use_typo_metrics:
                    self.assertEqual(
                        l_font['OS/2'].sTypoAscender,
                        norm_m(r_font['OS/2'].usWinAscent, r_upm, l_upm),
                        "Local %s typoAscender %s is not equal to remote %s winAscent %s" % (
                            style,
                            l_font['OS/2'].sTypoAscender,
                            style,
                            norm_m(r_font['OS/2'].usWinAscent, r_upm, l_upm),
                        )
                    )
                    self.assertEqual(
                        l_font['OS/2'].sTypoDescender,
                        - norm_m(r_font['OS/2'].usWinDescent, r_upm, l_upm),
                        "Local %s typoDescender %s is not equal to remote %s winDescent -%s" % (
                            style,
                            l_font['OS/2'].sTypoDescender,
                            style,
                            norm_m(r_font['OS/2'].usWinDescent, r_upm, l_upm),
                        )
                    )
                    self.assertEqual(
                        l_font['OS/2'].sTypoLineGap,
                        0,
                        "Local %s typoLineGap %s is not equal to 0" % (
                            style,
                            l_font['OS/2'].sTypoLineGap
                        )
                    )

                self.assertEqual(
                    l_font['hhea'].ascent, 
                    norm_m(r_font['hhea'].ascent, r_upm, l_upm),
                    "Local %s hheaAscender %s is not equal to remote %s hheaAscender %s" % (
                        style,
                        l_font['hhea'].ascent, 
                        style,
                        norm_m(r_font['hhea'].ascent, r_upm, l_upm),
                    )
                )
                self.assertEqual(
                    l_font['hhea'].descent, 
                    norm_m(r_font['hhea'].descent, r_upm, l_upm),
                    "Local %s hheaDescender %s is not equal to remote %s hheaDescender %s" % (
                        style,
                        l_font['hhea'].descent,
                        style,
                        norm_m(r_font['hhea'].descent, r_upm, l_upm),
                    )
                )
                self.assertEqual(
                    l_font['hhea'].lineGap,
                    norm_m(r_font['hhea'].lineGap, r_upm, l_upm),
                    "Local %s hheaLineGap %s is not equal to remote %s hheaLineGap %s" % (
                        style,
                        l_font['hhea'].lineGap,
                        style,
                        norm_m(r_font['hhea'].lineGap, r_upm, l_upm),
                    )
                )


class TestVerticalMetrics(TestGlyphsFiles):
    
    def test_family_has_vertical_metric_parameters(self):
        """Check family has vertical metric custom parameters

        Vertical metrics custom parameters are needed because these need to
        be set manually. They should not be calculated by Glyphsapp."""
        for font in self.fonts:
            masters = font.masters
            for master in masters:
                master_vert_params = set([p.name for p in master.customParameters])
                required_vert_params = set([p for p in VERT_KEYS])
                missing_vert_params = required_vert_params - master_vert_params
                self.assertEqual(
                    set([]),
                    missing_vert_params,
                    ("%s master is missing the following vertical metric "
                     "custom parameters [%s]") % (
                         master.name,
                         ', '.join(missing_vert_params),
                     )
                )

    def test_family_has_use_typo_metrics_enabled(self):
        """Check family has 'Use Typo Metrics' enabled"""
        for font in self.fonts:
            self.assertEqual(
                font.customParameters['Use Typo Metrics'],
                True,
                ("Font must have custom parameter 'Use Typo Metrics' "
                 "enabled.\n\n"
                 "Add the custom parameter font.customParameters"
                 "['Use Typo Metrics'].")
            )

    def test_family_share_same_metric_values(self):
        """Check each instance has same vertical metric values"""
        if not self.remote_font:
            font_master1_params = self.fonts[0].masters[0].customParameters

            for font in self.fonts:
                for master in font.masters:
                    for param in master.customParameters:
                        if param.name in VERT_KEYS:
                            self.assertEqual(
                                font_master1_params[param.name],
                                master.customParameters[param.name],
                                ("Vertical metrics are not family wide "
                                 "consistent.\n\n"
                                 "%s %s %s is not equal to %s") % (
                                    master.name,
                                    param.name,
                                    master.customParameters[param.name],
                                    font_master1_params[param.name],
                                )
                            )


    def test_win_ascent_and_win_descent_equal_bbox(self):
        """Check Win Ascent and Win Descent equal yMax, yMin of bbox

        MS recommends OS/2's win Ascent and win Descent must be the ymax
        and ymin of the bbox"""
        family_ymax_ymin = []
        for font in self.fonts:
            ymin, ymax = shortest_tallest_glyphs(font)
            family_ymax_ymin.append(ymin)
            family_ymax_ymin.append(ymax)

        ymax = max(family_ymax_ymin)
        ymin = min(family_ymax_ymin)

        for font in self.fonts:
            for master in font.masters:
                win_ascent = master.customParameters['winAscent']
                win_descent = master.customParameters['winDescent']
                self.assertEqual(
                    int(win_ascent),
                    ymax,
                    ("%s master's winAscent %s is not equal to yMax %s") % (
                        master.name,
                        win_ascent,
                        ymax)
                )
                # ymin is abs because win descent is a positive integer
                self.assertEqual(
                    int(win_descent),
                    abs(ymin),
                    ("%s master's winDescent %s is not equal to yMin %s") % (
                        master.name,
                        win_descent,
                        abs(ymin))
                )


class TestRepositoryStructure(TestGlyphsFiles):
    """Repositories must conform to the following tree:

        .
    ├── AUTHORS.txt
    ├── CONTRIBUTORS.txt
    ├── DESCRIPTION.en_us.html
    ├── FONTLOG.txt
    ├── METADATA.pb
    ├── OFL.txt
    ├── README.md
    ├── fonts
    │   └── ttf
    │       ├── Inconsolata-Bold.ttf
    │       └── Inconsolata-Regular.ttf
    └── sources
        └──  Inconsolata.glyphs

    """
    def test_repo_in_gf_upstream_repos_doc(self):
        """Check the family is in GF Upstream document"""
        found = False
        for font in self.fonts:
            if self.repo_doc.has_family(font.familyName):
                found = True
            self.assertEqual(
                True,
                found, 
                ("Family is not listed in the GF Master repo doc, %s.\n\n"
                 "Listing the family helps us keep track of it and ensure "
                 "there is one original source") % UPSTREAM_REPO_DOC
            )

    def test_fonts_dir_exists(self):
        """Check 'fonts' directory exists"""
        abs_fonts_folder = os.path.join(project_dir, FONTS_FOLDER)
        self.assertEquals(
            True,
            os.path.isdir(abs_fonts_folder),
            ("'%s' folder is missing or named incorrectly.\n\n"
             "Font binaries should be generated into this folder. "
             "Sub folders for 'ttf', 'otf', 'web' are allowed.") % (
                 abs_fonts_folder
            )
        )

    def test_sources_dir_exists(self):
        """Check 'sources' directory exists"""
        abs_sources_folder = os.path.join(project_dir, SOURCES_FOLDER)
        self.assertEquals(
            True,
            os.path.isdir(abs_sources_folder),
            ("'%s' folder is missing or named incorrectly.\n\n"
             "Source files must be stored here. There should only be "
             "one definitive source. Version control allows us to access "
             "previous version (we can rewind history if needed).\n\n"
             "Naming files using the following convention is banned, "
             "family-regular_AA|AB.ttf.") % abs_sources_folder
        )

    def test_contributors_file_exists(self):
        """Check 'CONTRIBUTORS.txt' exists"""
        self.assertIn(
            'CONTRIBUTORS.txt',
            os.listdir(project_dir),
            ("'CONTRIBUTORS.txt' is missing in parent directory.\n\n"
             "Use https://raw.githubusercontent.com/Gue3bara/Cairo/master/CONTRIBUTORS.txt "
             "as a reference to make your own.")
        )

    def test_authors_file_exists(self):
        """Check 'AUTHORS.txt' exists"""
        self.assertIn(
            'AUTHORS.txt',
            os.listdir(project_dir),
            ("'AUTHORS.txt' is missing in parent directory.\n\n"
             "Use https://raw.githubusercontent.com/Gue3bara/Cairo/master/AUTHORS.txt "
             "as a reference to make your own.")
        )

    def test_ofl_first_line_matches_copyright(self):
        """Check OFL.txt first line matches the copyright string"""
        for font in self.fonts:
            ofl_txt_path = os.path.join(project_dir, 'OFL.txt')
            with open(ofl_txt_path) as ofl_doc:
                ofl_copyright = ofl_doc.readlines()[0][:-1] # ignore linebreak
                self.assertEqual(
                    font.copyright,
                    ofl_copyright,
                    ("OFL.txt and font copyright do not match.\n\n"
                     "OFL copyright: %s\n"
                     "Font copyright: %s\n") % (font.copyright, ofl_copyright)
                )


if __name__ == '__main__':
    Glyphs.showMacroWindow()
    __glyphsfile = Glyphs.font.filepath
    project_dir = os.path.abspath(
        os.path.join(os.path.dirname(__glyphsfile), '..')
    )
    if len(set([f.familyName for f in Glyphs.fonts])) == 1:
        TestProgram(argv=['--verbose'], exit=False, testRunner=GlyphsTestRunner)
    else:
        print 'Multiple Families open! Please only have one family open'
