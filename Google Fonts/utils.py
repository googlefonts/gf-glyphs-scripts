from fontTools.ttLib import TTFont
from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen
import csv


API_URL_PREFIX = 'https://fonts.google.com/download?family='
UPSTREAM_REPO_DOC = 'http://tinyurl.com/kflp3k7'
UPSTREAM_REPO_URLS = 'http://tinyurl.com/kd9lort'


def ttf_family_style_name(ttfont):
    try: # Does font have mac ps names?
        ps_name = ttfont['name'].getName(6, 1, 0, 0).string
        ps_name = ps_name.split('-')
    except: # else use win ps name
        ps_name = ttfont['name'].getName(6, 3, 1, 1033).string
        ps_name = psn_name.decode('utf_16_be').split('-')
    try:
        family, style = ps_name
        return family, style
    except:
        return ps_name, 'Regular'


def convert_camelcase(name, seperator=' '):
    """ExtraCondensed -> Extra Condensed"""
    return re.sub('(?!^)([A-Z]|[0-9]+)', r'%s\1' % seperator, name)


def _font_family_url(family_name):
    '''Create the url to download a font family'''
    family_name = str(family_name).replace(' ', '%20')
    url = '%s%s' % (API_URL_PREFIX, family_name)
    return url


def url_200_response(family_name):
    """Return a zipfile containing a font family hosted on fonts.google.com"""
    family_url = _font_family_url(family_name)
    request = urlopen(family_url)
    if request.getcode() == 200:
        return request
    else:
        return False


def fonts_from_zip(zipfile):
    '''return a list of fontTools.ttLib TTFont objects'''
    ttfs = []
    for file_name in zipfile.namelist():
        if 'ttf' in file_name:
            ttfs.append(TTFont(zipfile.open(file_name)))
    return ttfs


def download_gf_family(name):
    remote_fonts = url_200_response(name)
    if remote_fonts:
        family_zip = ZipFile(StringIO(remote_fonts.read()))
        return fonts_from_zip(family_zip)


class RepoDoc:
    """return the Google Repo doc which contains all repo urls"""
    handle = urlopen(UPSTREAM_REPO_URLS)
    ss = StringIO(handle.read())
    _doc = list(csv.DictReader(ss))

    @property
    def doc(self):
        return self._doc

    def has_family(self, familyname):
        families = [r['family'] for r in self._doc]
        if familyname in families:
            return True
        return False

    def family_url(self, familyname):
        for row in self._doc:
            if str(row['family']) == str(familyname):
                return row['upstream']
        return None
