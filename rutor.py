# -*- coding: utf-8 -*-
#VERSION: 1.4
#AUTHORS: Anatoly Mayorov (mmajor@yandex.ru), Konstantin Lebedev (whitef0x@ya.ru)
# This plugin is licensed under the GNU GPL Version 2.

from novaprinter import prettyPrinter
from helpers import download_file, htmlentitydecode
import http.cookiejar
import re
import gzip
from io import StringIO
import urllib.parse
import urllib.request
import os
import logging

'''
<tr class="gai"><td>12&nbsp;Дек&nbsp;14</td><td ><a class="downgif" href="http://d.rutor.org/download/397232"><img src="http://s.rutor.org/i/d.gif" alt="D" /></a><a href="magnet:?xt=urn:btih:fc3ce688c351b60862da9dfa23953008ee1c1a33&dn=rutor.org&tr=udp://bt.rutor.org:2710&tr=http://retracker.local/announce"><img src="http://s.rutor.org/i/m.png" alt="M" /></a>
<a href="/torrent/397232/oddworld-strangers-wrath-2014-android">Oddworld: Stranger&#039;s Wrath (2014) Android </a></td> <td align="right">4<img src="http://s.rutor.org/i/com.gif" alt="C" /></td>
<td align="right">4.26&nbsp;GB</td><td align="center"><span class="green"><img src="http://s.rutor.org/t/arrowup.gif" alt="S" />&nbsp;44</span>&nbsp;<img src="http://s.rutor.org/t/arrowdown.gif" alt="L" /><span class="red">&nbsp;17</span></td></tr>
'''

torrent_pattern = re.compile(r'''<tr class=".*"><td>.*</td><td.*><a class="downgif" href="(?P<link>.+)"><img src=".+" alt="D" /></a><a href=".+"><img src=".+" alt="M" /></a>\s*<a href="(?P<desc_link>.+)">(?P<name>.+)?\s</a></td>\s*(<td align="right">.+<img.*></td>)?\s*<td align="right">(?P<size>.+)</td><td align="center"><span class="green"><img src=".+" alt="S" />.*(?P<seeds>\d+)</span> <img src=".*" alt="L" /><span class="red">.*(?P<leech>\d+)</span></td></tr>''')

tag = re.compile(r'<.*?>')


class rutor(object):
    
    ''' RUTOR.ORG Russian free tracker '''
    url = 'http://www.rutor.info/'
    name = 'rutor.org'
    supported_categories = {'all': 0,
                            'movies': 1,
                            'tv': 6,
                            'music': 2,
                            'games': 8,
                            'anime': 10,
                            'software': 9,
                            'pictures': 3,
                            'books': 11}

    query_pattern = '%(url)s/search/%(start)i/%(f)i/000/2/%(q)s'
    cookie_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),name + ".cookies")
    cookie_pattern = re.compile(r'''document.cookie.indexOf\('(?P<name>.+)=(?P<value>.+)'\)''')

    def __init__(self):
        pass

    def download_torrent(self, info): 
        print(download_file(info, info))


    def retrieve_url(self,url):
        cj = http.cookiejar.MozillaCookieJar(self.cookie_filename)
        if os.access(self.cookie_filename, os.F_OK):
            cj.load()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        req = urllib.request.Request(url)
        response = opener.open(req)
        dat = response.read()
        # Check if it is gzipped
        if dat[:2] == '\037\213':
            # Data is gzip encoded, decode it
            compressedstream = StringIO.StringIO(dat)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            dat = gzipper.read()

        # document.cookie.indexOf('_ddn_intercept_2_=ebdc811923afde6a39f0d7bc77dfe97d')
 
        m = re.search(self.cookie_pattern, dat.decode('utf-8'))
        if m:
            #opener.addheaders.append(('Cookie', m.group('cookie')))
            ck = http.cookiejar.Cookie(version=0, name=m.group('name'), value=m.group('value'), port=None, port_specified=False, domain=self.name, domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
            cj.set_cookie(ck)
            cj.save(self.cookie_filename, ignore_discard=True, ignore_expires=True)
            response = opener.open(req)
            dat = response.read()


        info = response.info()
        charset = 'utf-8'
        try:
            ignore, charset = info['Content-Type'].split('charset=')
        except:
            pass
        dat = dat.decode(charset, 'replace')
        dat = htmlentitydecode(dat)
        return dat.encode('utf-8', 'replace')

    def search_page(self, what, cat, start):
        params = {'url': self.url,
                'q': urllib.parse.quote(what),
                'f': self.supported_categories[cat],
                'start': start}
        dat = self.retrieve_url(self.query_pattern % params).decode('utf-8')
        for el in torrent_pattern.finditer(dat):
            d = el.groupdict()
            d['desc_link'] = self.url + d['desc_link']
            d['engine_url'] = self.url
            d['name'] = tag.sub('', d['name'])
            yield d

    def search(self, what, cat='all'):
        start = 0
        f = True
        while f:
            f = False
            for d in self.search_page(what, cat, start):
                if __name__ != "__main__":
                    prettyPrinter(d)
                f = True
            start += 1

# For testing purposes.
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    engine = rutor()
    engine.search('friends')
