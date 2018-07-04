#VERSION: 1.00
#AUTHORS:lima66

try:
    # python3
    from html.parser import HTMLParser
except ImportError:
    # python2
    from HTMLParser import HTMLParser

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file


class btetree(object):
    url = "http://bt.etree.org/"
    name = "bt.etree"
    supported_categories = {'all': 'all',
                            'music': 'music',
                            'others': 'others'}

    def download_torrent(self, info):
        print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """
        A, TD, TR, TABLE = ('a', 'td', 'tr', 'table')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = {}  # dict for found item
            self.item_name = None  # key's name in current_item dict
            self.page_empty = 29500
            self.inside_tr = False
            self.find_data = False
            self.check_size = False

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)

            if tag == self.TR and params.get('align') == 'right':
                self.inside_tr = True
                self.current_item = {}
            if not self.inside_tr:
                return

            if "href" in params:
                link = params["href"]
                if params.get('class') == 'details_link':
                    if tag == self.A and link.startswith('details.php'):
                        self.current_item["desc_link"] = "".join((self.url, link))
                        self.current_item["engine_url"] = self.url
                        self.item_name = "name"
                        self.find_data = True

                elif link.startswith('download.php'):
                    self.current_item["link"] = "".join((self.url, link))

                elif link.endswith('#startcomments'):
                    self.item_name = "size"
                    self.find_data = True
                    self.check_size = True

                elif link.endswith('#seeders'):
                    self.item_name = "seeds"
                    self.find_data = True

                elif link.endswith('#leechers'):
                    self.item_name = "leech"
                    self.find_data = True

        def handle_data(self, data):
            if self.inside_tr and self.item_name and self.find_data and not self.check_size:
                self.find_data = False
                self.current_item[self.item_name] = data.strip().replace(',', '')
            elif self.inside_tr and self.item_name and self.find_data and self.check_size:
                if data.endswith('MB') or data.endswith('GB'):
                    self.check_size = False
                    self.current_item[self.item_name] = data.strip()
                    self.item_name = None

        def handle_endtag(self, tag):
            if self.inside_tr and tag == self.TR:
                self.inside_tr = False
                self.item_name = None
                self.find_data = False
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
        """http://bt.etree.org/index.php?searchzz=test&cat&page=50"""
        number_page = 0
        while number_page <= 200:
            page = "".join((self.url, "/index.php?searchzz={0}&cat&sort=seeders&page={1}")).format(query, number_page)
            html = retrieve_url(page)
            length_html = len(html)
            if length_html <= parser.page_empty:
                break

            parser.feed(html)
            number_page += 50

        parser.close()
