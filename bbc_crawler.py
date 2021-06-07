import re
import itertools
import urllib.request
import os
import time
import wget
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib.parse import urljoin

def download(url, user_agent='wswp', retry=3, charset='utf-8'):
    #print("download ", url)
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)
    try:
        resp = urllib.request.urlopen(request)
        cs = resp.headers.get_content_charset()
        if not cs:
            cs = charset
        html = resp.read().decode(cs)
    except(URLError,HTTPError,ContentTooShortError)as e:
        print('Download error:', e.reason)
        html =None
        if retry > 0:
            if hasattr(e,'code') and 500 <= e.code < 600:
                # recursively retry 5xx HTTP errors
                return download(url, retry-1)
    return html

def crawl_episode(sitemap):
    links = re.findall(r'<h2><a  href="/learningenglish/chinese/features/take-away-english/ep.*">', sitemap)
    links = list(map(lambda x: re.findall(r'"([^"]*)"', x), links))
    links = list(itertools.chain(*links))
    links = [urljoin('https://www.bbc.co.uk', x) for x in links]
    return links


def download_pdf_mp3(article, store_path='D:\\python\\bbc_takeway'):
    print(article)
    html = download(article)
    pdf_link = re.findall(r'<a class="download bbcle-download-extension-pdf" href="(.*?)"><span', html)
    print('pdf link ', pdf_link)
    mp3_link = re.findall(r'<a class="download bbcle-download-extension-mp3" href="(.*?)"><span', html)
    print('mp3 link ', mp3_link)
    if len(pdf_link) == 0 or len(mp3_link) == 0:
        return
    pdf_file = os.path.join(store_path, os.path.basename(pdf_link[0]))
    mp3_file = os.path.join(store_path, os.path.basename(mp3_link[0]))
    if not os.path.exists(pdf_file):
        wget.download(pdf_link[0], pdf_file)
        #urllib.request.urlretrieve(pdf_link[0], pdf_file)
    if not os.path.exists(mp3_file):
        wget.download(mp3_link[0], mp3_file)
        #urllib.request.urlretrieve(pdf_link[0], mp3_file)

if __name__ == "__main__":
    html = download("https://www.bbc.co.uk/learningenglish/chinese/features/take-away-english")
    articles = crawl_episode(html)
    i = 0
    for a in articles:
        if i > 100:
            print('Only download 100 articles')
            break
        download_pdf_mp3(a)
        time.sleep(1)
        ++i
