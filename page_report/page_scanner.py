"""scan a web page and provided statistics"""

import re
from collections import namedtuple, Counter
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from bs4.element import NavigableString
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
N_COMMON = 5
META = 'meta'
PARAGRAPH = 'p'

TEMPLATE_DIR = 'templates'
REPORT_TEMPLATE = 'page_report.html'


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
        self.tag_count = len(self.metas)
        self.links = self.link_destinations_and_text()
        self.keywords = self.meta_keywords()
        self.total_words = len(self.words)
        self.unique_words = Counter(self.words)
        self.unique_word_count = len(self.unique_words)
        ranked_words = self.unique_words.most_common(N_COMMON)
        self.common_words = [tup[0] for tup in ranked_words]


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
        i = 0
        bare_links = self.soup.find_all(LINK)
        links = []
        for link in bare_links:
            href = link.get('href')
            content = link.contents
            title = link.get('title')
            alttxt = link.get('alt')
            if content and isinstance(content[0], NavigableString):
                text = content[0]
            elif title:
                text = title
            elif alttxt:
                text = alttxt
            else:
                text = ''
            links.append(Link(href=href, text=text))
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
    print('filesize {} KB'.format(kb))
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


def render_report(url):
    soup, kbs = soup_from(url)
    parsed = SoupParser(soup)
    for_template = {
        'url': url,
        'title': parsed.title,
        'tag_count': parsed.tag_count,
        'page_size_kb': kbs,
        'word_count': parsed.total_words,
        'unique_words': parsed.unique_words,
        'unique_word_count': parsed.unique_word_count,
        'ranked_words': parsed.common_words,
        'links': parsed.links
    }
    template = load_template()
    htmlout = template.render(for_template)
    return htmlout


def load_template():
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(REPORT_TEMPLATE)
    return template


def save_report(rendered_template, outfile):
    with open(outfile, 'wb') as file_:
        file_.write(rendered_template.encode('utf-8'))

def report_for(url, report_file):
    rendered = render_report(url)
    save_report(rendered, report_file)
