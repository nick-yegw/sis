import os,re
import threading
from scrapy.contrib.spiders import Rule, CrawlSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from scrapy.selector import Selector

try:
    import urllib.request
    #import urllib.parse
except ImportError:
    import urllib

    urllib.request = __import__('urllib2')
    urllib.parse = __import__('urlparse')

urlopen = urllib.request.urlopen
request = urllib.request.Request

__author__ = 'Administrator'


class DownloadThread(threading.Thread):

    url = filename = None

    def __init__(self, url, filename):
        threading.Thread.__init__(self)
        self.url = url
        self.filename = filename

    def run(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            return
        #filename = get_valid_filename(filename)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0'}
        req = request(self.url, headers=headers)
        try:
            data = get_data_from_req(req)
            if data is '':
                return
            f = open(self.filename, 'wb')
            f.write(data)
            f.close()
        except Exception as e:
            print(e)
        return


class SisSpider(CrawlSpider):

    download_delay = 1

    def __init__(self, *a, **kw):
        super(SisSpider, self).__init__(*a, **kw)
        if not os.path.exists(self.wtfdir):
            os.mkdir(self.wtfdir)

    wtfdir = 'E:/python/Python_Project/sis/test/'
    name = "sis"
    allowed_domains = ['38.103.161.147']
    start_urls = [
        'http://38.103.161.147/forum/forumdisplay.php?fid=230',
        'http://38.103.161.147/forum/forumdisplay.php?fid=143'
    ]
    base_url = 'http://38.103.161.147/forum/'

    rules = (
        # Rule(sle(allow=("/forum/$", )), follow=True),
        # Rule(sle(allow=("/forum/[^/]+/?$", )), follow=True),
        Rule(sle(allow=('/forum/forum-230-\d{1,2}\.html', ))),
        Rule(sle(allow=('thread-\d*-1-1.html', )), callback='parse_item')
        #Rule(sle(allow=('/forum/forum-143-\d{1,2}\.html', )))
    )

    # def my_process_links(self, links):
    #     result = []
    #     for link in links:
    #         m = re.search(r'/forum/forum-230-\d{1,2}\.html', link)
    #         if m:
    #             result.append(link)
    #     return result

    def parse_item(self, response):
        # cwd = os.getcwd()
        # os.chdir(self.wtfdir)
        sel = Selector(response)
        try:
            title = self.wtfdir + sel.xpath('//form/div/h1/text()').extract()[0].strip().encode() + "/"
        except:
            return
        if not os.path.exists(title):
            os.makedirs(title)

        imgs = sel.xpath('//form/div[1]//div/img/@src').extract()
        torrents = sel.xpath('//a[contains(text(), "torrent")]/@href').extract()
        torrent_names = sel.xpath('//a[contains(text(), "torrent")]/text()').extract()

        if len(imgs) == 0 and len(torrents) == 0:
            os.rmdir(title)
            return

        for img in imgs:
            DownloadThread(img.encode(), title + get_valid_filename(os.path.basename(img))).start()
            #down_link(img.encode(), title + get_valid_filename(os.path.basename(img)))

        for i in xrange(len(torrents)):
            DownloadThread(self.base_url + torrents[i].encode(), title + get_valid_filename(torrent_names[i].encode())).start()
            #down_link(self.base_url + torrents[i].encode(), title + get_valid_filename(torrent_names[i].encode()))
        return


def get_valid_filename(filename):
    keepcharacters = (' ', '.', '_', '-')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


def down_link(url, filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        return
    #filename = get_valid_filename(filename)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0'}
    req = request(url, headers=headers)
    try:
        data = get_data_from_req(req)
        if data is '':
            return
        f = open(filename, 'wb')
        f.write(data)
        f.close()
    except Exception as e:
        print(e)
    return


def get_data_from_req(req):
    attempts = 0
    binary = ''
    while attempts < 10:
        try:
            binary = urlopen(req).read()
            break
        except Exception as e:
            attempts += 1
            print(e)
    return binary