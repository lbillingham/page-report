"""scan a web page and provided statistics"""

import re
from collections import namedtuple, Counter
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from requests import get
# HTTPError will look unused
#  but import here so client code
#   need not know about requests
from requests import  HTTPError # pylint: disable=unused-import


def soup_from(url):
    """
    return the page parsed by BeautifulSoup

    url: is a pre-validated url as as string

    raises: HTTP error if don't get valid response
    """
    resp = get(url)
    resp.raise_for_status()
    bare_text = resp.content.decode(resp.encoding)
    soup = BeautifulSoup(bare_text, 'lxml')
    size_kb = len(resp.content) // 1024
    return soup, size_kb

CONTENT = 'content'
LINK = 'a'
KEYWORDS_ATTR = {'name':'keywords'}
META = 'meta'
PARAGRAPH = 'p'


Link = namedtuple('Link', ['href', 'text'])

class SoupParser(object):
    """
    Take page soup and extract meaning
    soup: the BeautifulSoup from a web page

    attributes
    words: list of words on page
    metas: list of all meta tags on page
    links: list of (href, text) for all links in page
    """
    def __init__(self, soup):
        self.soup = soup
        self.title = self.soup.find('title').contents[0]
        self.words = self.paragraph_words()
        self.metas = self.meta_tags()
        self.links = self.link_destinations_and_text()
        self.keywords = self.meta_keywords()
        self.total_words = len(self.words)
        word_count = Counter(self.words)
        self.unique_words = len(word_count)
        self.common_words = [tup[0] for tup in word_count]


    def paragraph_words(self):
        """
        list of all words on
        page paragraph content
        """
        words_regex = r"[\w']+"
        paras_text = ' '.join(
            para.get_text() for para in self.soup.find_all(PARAGRAPH)
        )
        words = re.findall(words_regex, paras_text.lower())
        return words

    def meta_tags(self):
        """list all meta tags on page"""
        metas = self.soup.find_all(META)
        nested_meta_keys = [list(m.attrs.keys()) for m in metas]
        meta_keys = [item for sublist in nested_meta_keys for item in sublist]
        return meta_keys

    def link_destinations_and_text(self):
        """
        list of named tuples of links
        hrefs and text
        """
        bare_links = self.soup.find_all(LINK)
        links = [
            Link(
                href=link.get('href'), text=link.get('text')) for link in bare_links
        ]
        return links

    def meta_keywords(self):
        """list of keywords from meta tags"""
        all_kws = self.soup.find_all(attrs=KEYWORDS_ATTR)
        kw_str = ','.join(kw.attrs.get(CONTENT) for kw in all_kws)
        kws = [v.strip() for v in kw_str.split(',')]
        return kws

def print_report(url):
    soup, kb = soup_from(url)
    template = load_template()
    parsed = SoupParser(soup)
    print('Page', url)
    print('Title', parsed.title)
    print('All Meta Tags', parsed.metas)
    print('filesize {}KB'.format(kb))
    print('word count', parsed.total_words)
    print('number of unique words', parsed.unique_words)
    print('most common words: {}'.format(parsed.common_words))

    metas_not_present = []
    for kw in parsed.keywords:
        if kw not in parsed.words:
            metas_not_present.append(kw)
    print('keywords not in text ', metas_not_present)
    print ('Links')
    print ('destination, text')
    for hr, tx in parsed.links:
        print(hr, tx)

def load_template():
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('page_report.html')
    return template


def save_report(template, template_vars):
    htmlout = template.render(template_vars)
    with open('./outfile.html', 'w') as file_:
        file_.write(htmlout)