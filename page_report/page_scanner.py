"""scan a web page and provided statistics"""
from bs4 import BeautifulSoup
from requests import get, HTTPError

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
    return soup
