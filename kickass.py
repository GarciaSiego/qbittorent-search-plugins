#VERSION: 0.2.1
#AUTHORS: Charitoo Dunamis (charitoodunamis@gmail.com)
#LICENSE: GNU GPL v3

import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

try:
    import sys
    from os.path import dirname, abspath, join as path_join

    lib_dir = abspath(dirname(dirname(__file__)))
    lib_dir = path_join(lib_dir, 'qbt')
    logging.debug("%s" % path_join(lib_dir, 'qbt'))
    sys.path.insert(0, lib_dir)
    from helpers import retrieve_url
    from novaprinter import prettyPrinter
except ImportError:
    from helpers import retrieve_url
    from novaprinter import prettyPrinter

BASES = 1024
SIZES = {"KiB": BASES, "MiB": BASES**2, "GiB": BASES**3}
URL = "https://kickass.cd"


class KickassHtmlParser(HTMLParser):
    cur_torrent = None
    cur_css_class = None
    processed_data = {
        "cellMainLink": "name",
        "green center": "seeds",
        "red lasttd center": "leech",
        "nobr center": "size"
    }

    def __init__(self, res=[], url=URL):
        try:
            super().__init__()
        except:
            HTMLParser.__init__(self)
        self.results = res
        self.total = 0
        self.cur_class = ""
        self.curr = None

    def handle_starttag(self, tag, attrs):
        params = dict(attrs)
        self.cur_class = params.get("class", None)
        href = params.get("href", None)

        if tag == "tr" and self.curr is None:
            self.curr = {"engine_url": URL}

        elif tag == "a" and self.cur_class == "cellMainLink":
            self.curr["desc_link"] = URL + href

        elif self.cur_class == "icon16" and params.get('data-nop', '') is None:
            self.curr["link"] = href
        else:
            if tag == "a":
                logging.debug("Params: %s" % params)

    def handle_endtag(self, tag):
        if self.curr and tag == "tr":
            if len(self.curr) != 7:
                return
            self.total += 1
            self.results.append(self.curr)
            self.curr = None

    def handle_data(self, data):
        key = self.processed_data.get(self.cur_class, None)
        data = data.strip()
        if key and data:
            if key == "size":
                try:
                    num, power = data.split(u"\xa0")
                    data = int(float(num) * SIZES.get(power, 1))
                except ValueError:
                    data = 0
            try:
                self.curr[key] = str(data)
            except UnicodeEncodeError:
                self.curr[key] = unicode(data)


class kickass(object):

    url = URL
    name = "Kickass"
    search_url = url + "/usearch/{query}{category}/{page}/"
    supported_categories = {'movies': 'movies', 'tv': 'tv', 'music': 'music',
                            'games': 'games', 'software': 'applications',
                            'pictures': 'other', 'all': ''}
    results = []
    parser = KickassHtmlParser(res=results, url=url)

    def search(self, what, cat='all'):
        page = 1
        category = " category:{}".format(cat) if cat else ""
        while page <= 2:
            url = self.search_url.format(query=what, category=category,
                                         page=page)
            page_content = retrieve_url(url)
            self.parser.feed(page_content)
            page += 1
        self.results = self.parser.results
        self.parser.close()
        for torrent in self.results:
            prettyPrinter(torrent)


if __name__ == "__main__":
    from pprint import pprint
    t = kickass()
    t.search("magnum")
    for torrent in t.results:
        pprint(torrent)
