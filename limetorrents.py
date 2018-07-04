#VERSION: 3.09
#AUTHORS: Lima66

try:
    # python3
    from html.parser import HTMLParser
except ImportError:
    # python2
    from HTMLParser import HTMLParser

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file


class limetorrents(object):
    url = "https://www.limetorrents.cc"
    name = "LimeTorrents"
    supported_categories = {'all': 'all',
                            'anime': 'anime',
                            'software': 'applications',
                            'games': 'games',
                            'movies': 'movies',
                            'music': 'music',
                            'tv': 'tv'}

    def download_torrent(self, info):
        print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """

        def error(self, message):
            pass

        A, TD, TR, HREF = ('a', 'td', 'tr', 'href')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = {}  # dict for found item
            self.item_name = None  # key's name in current_item dict
            self.page_empty = 22000
            self.inside_tr = False
            self.findTable = False
            self.parser_class = {"tdnormal": "size",  # class
                                 "tdseed": "seeds",
                                 "tdleech": "leech"}

        def handle_starttag(self, tag, attrs):

            params = dict(attrs)
            if params.get('class') == 'table2':
                self.findTable = True

            if tag == self.TR and self.findTable and (params.get('bgcolor') == '#F4F4F4' or params.get('bgcolor') == '#FFFFFF'):
                self.inside_tr = True
                self.current_item = {}
            if not self.inside_tr:
                return

            if self.inside_tr and tag == self.TD:
                if "class" in params:
                    self.item_name = self.parser_class.get(params["class"], None)
                    if self.item_name:
                        self.current_item[self.item_name] = -1

            if self.inside_tr and tag == self.A and self.HREF in params:
                link = params["href"]
                if link.startswith("http://itorrents.org/torrent/"):
                    self.current_item["link"] = link
                    self.current_item["engine_url"] = self.url
                    self.item_name = "name"
                elif link.endswith(".html"):
                    self.current_item["desc_link"] = self.url + link

        def handle_data(self, data):
            if self.inside_tr and self.item_name:
                if self.item_name == 'size' and (data.endswith('MB') or data.endswith('GB')):
                    self.current_item[self.item_name] = data.strip().replace(',', '')
                elif not self.item_name == 'size':
                    self.current_item[self.item_name] = data.strip().replace(',', '')

                self.item_name = None

        def handle_endtag(self, tag):
            if tag == 'table':
                self.findTable = False

            if self.inside_tr and tag == self.TR:
                self.inside_tr = False
                self.item_name = None
                array_length = len(self.current_item)
                if array_length < 1:
                    return
                prettyPrinter(self.current_item)
                self.current_item = {}

    def search(self, query, cat='all'):
        """ Performs search """
        query = query.replace("%20", "-")

        parser = self.MyHtmlParser(self.url)
        i = 1
        while True:
            page = "{0}/search/{1}/{2}/seeds/{3}".format(self.url, self.supported_categories[cat], query, i)
            html = retrieve_url(page)
            lunghezza_html = len(html)
            if lunghezza_html <= parser.page_empty:
                return
            parser.feed(html)
            i += 1
        parser.close()



