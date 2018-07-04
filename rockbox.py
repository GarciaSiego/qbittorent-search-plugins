#VERSION: 1.01
#AUTHORS:lima66

try:
    # python3
    from html.parser import HTMLParser
except ImportError:
    # python2
    from HTMLParser import HTMLParser

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file


class rockbox(object):
    url = "http://psychocydd.co.uk/"
    name = "RockBox"
    supported_categories = {'all': 'all',
                            'music': 'music',
                            'others': 'others'}

    def download_torrent(self, info):
        print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """
        A, TD, TR, SPAN = ('a', 'td', 'tr','span')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = {}  # dict for found item
            self.item_name = None  # key's name in current_item dict
            self.page_empty = 17500
            self.inside_tr = False
            self.find_data = False
            self.check_size = False
            self.name_Torrent = ""
            self.end_name = False
            self.seed_found = False
            self.leech_found = False

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)

            if "href" in params:
                link = params["href"]
                if tag == self.A and link.startswith('torrents.php?category'):
                    self.inside_tr = True
                    self.current_item = {}
            if not self.inside_tr:
                return

            if "href" in params:
                link = params["href"]
                if tag == self.A and link.startswith('details.php') and not link.endswith('#comments'):
                    self.current_item["desc_link"] = "".join((self.url, link))
                    self.current_item["engine_url"] = self.url
                    self.item_name = "name"
                    self.find_data = True

                elif link.startswith('download.php'):
                    self.current_item["link"] = "".join((self.url, link))
                    self.item_name = "size"
                    self.find_data = True
                    self.check_size = True

                elif link.startswith('peers.php?'):
                    if not self.seed_found:
                        self.seed_found = True
                        self.item_name = "seeds"
                        self.find_data = True
                    elif self.seed_found and not self.leech_found:
                        self.leech_found = True
                        self.item_name = "leech"
                        self.find_data = True

        def handle_data(self, data):
            if self.inside_tr and self.item_name and self.find_data and not self.check_size:
                if not self.item_name == 'name':
                    self.find_data = False
                    self.current_item[self.item_name] = data.strip().replace(',', '')
                    self.item_name = None
                elif self.end_name:
                    self.item_name = None
                    self.find_data = False
                    self.end_name = False
                    self.current_item["name"] = "%s %s" % (self.name_Torrent, data.strip())
                    self.name_Torrent = ""
                else:
                    self.name_Torrent = "%s %s" % (self.name_Torrent, data.strip())
                    self.find_data = False
            elif self.inside_tr and self.item_name and self.find_data and self.check_size:
                if data.endswith('MB') or data.endswith('GB'):
                    self.check_size = False
                    self.current_item[self.item_name] = data.strip()
                    self.item_name = None

        def handle_endtag(self, tag):
            if self.item_name == 'name' and tag == self.SPAN:
                self.find_data = True
                self.end_name = True

            if self.inside_tr and tag == self.TR:
                self.inside_tr = False
                self.item_name = None
                self.find_data = False
                self.seed_found = False
                self.leech_found = False
                array_length = len(self.current_item)
                if array_length < 1:
                    return
                prettyPrinter(self.current_item)
                self.current_item = {}

    def search(self, query, cat='all'):
        """ Performs search """
        cat_name = self.supported_categories.get(cat, None)
        if not cat_name:
            return

        parser = self.MyHtmlParser(self.url)

        query = query.replace("%20", "+")
        # http://psychocydd.co.uk/torrents.php?active=1&search=the+theory&&options=0&order=seeds&by=DESC&page=0
        number_page = 0
        while True:
            page = "".join((self.url, '/torrents.php?active=1&search={0}&&options=1&order=seeds&by=DESC&page={1}')).format(query, number_page)
            html = retrieve_url(page)
            length_html = len(html)
            if length_html <= parser.page_empty:
                return

            parser.feed(html)
            number_page += 1

        parser.close()
