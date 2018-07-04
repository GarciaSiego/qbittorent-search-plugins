#VERSION: 1.04
#AUTHORS: hoanns
# Chinese Gaming Tracker
# This thing is pretty straight forward.
# Beware that they sometimes upload uncracked games on here.

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

import re
# qBt
# noinspection PyUnresolvedReferences
from novaprinter import prettyPrinter
# noinspection PyUnresolvedReferences
from helpers import retrieve_url


# noinspection PyPep8Naming
class threedm(object):
    url = "http://bt.3dmgame.com/"
    name = "3dmgame"

    supported_categories = {'all': True,
                            'games': True,
                            'software': True}

    class Parsar(HTMLParser):

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = None
            self.save_data = None
            self.handle_that_data = False
            self.name_repl = re.compile("^\s*")

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                params = dict(attrs)
                try:
                    link = params["href"]
                    if link.startswith("down.php?"):
                        self.current_item = dict()
                        self.current_item["desc_link"] = self.url + link.replace("down.php", "show.php")
                        self.current_item["engine_url"] = self.url
                        self.current_item["link"] = self.url + link
                        self.save_data = "name"
                        self.handle_that_data = True
                except KeyError:
                    pass
            elif self.save_data == "name" and tag == "td":
                self.save_data = "size"
                self.handle_that_data = True
            elif self.save_data == "size" and tag == "span":
                self.save_data = "seeds"
                self.handle_that_data = True
            elif self.save_data == "seeds" and tag == "span":
                self.save_data = "leech"
                self.handle_that_data = True

        def handle_data(self, data):
            if self.handle_that_data:
                if self.save_data == "name":
                    if 'name' not in self.current_item:
                        self.current_item["name"] = ""
                    self.current_item["name"] += data
                else:
                    self.current_item[self.save_data] = data
                # all data collected
                if self.current_item.__len__() == 7:
                    # remove preceding whitespaces
                    self.current_item["name"] = self.name_repl.sub("", self.current_item["name"])
                    prettyPrinter(self.current_item)
                    self.current_item = None
                    self.save_data = None

        def handle_endtag(self, tag):
            # special case name: spans over multiple tags
            if self.save_data == "name":
                if tag == "a":
                    self.handle_that_data = False
            else:
                self.handle_that_data = False

    def search(self, what, cat='all'):

        query = "http://bt.3dmgame.com/search.php?keyword=" + what
        data = retrieve_url(query)

        parser = self.Parsar(self.url)
        parser.feed(data)

        del data
        return


if __name__ == "__main__":
    engine = threedm()
    engine.search('Handball.17', 'games')
