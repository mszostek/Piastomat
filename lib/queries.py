import logging
import urllib.parse

import requests

log = logging.getLogger(__name__)

UA = 'Piastomat/0.0 ([[User:Piastu]] pl.wikipedia.org, wikidata, mszostek@gmail.com); pywikibot'

QLEVER_URL = "https://qlever.dev/api/wikidata"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"


def query_qlever(sparql_query):
    """Execute a SPARQL query against QLever's Wikidata endpoint."""
    headers = {'User-Agent': UA, 'Accept': 'application/json'}
    try:
        response = requests.get(QLEVER_URL, params={'query': sparql_query, 'format': 'json'}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error("QLever query failed: %s", e)
        return None


def query_wikidata(sparql_query):
    """Execute a SPARQL query against the Wikidata SPARQL endpoint."""
    headers = {'User-Agent': UA, 'Accept': 'application/json'}
    try:
        response = requests.get(WIKIDATA_SPARQL_URL, params={'query': sparql_query, 'format': 'json'}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error("Wikidata SPARQL query failed: %s", e)
        return None


class WikidataAPI:
    """REST client for Wikidata's item search endpoint."""

    def __init__(self):
        self.base_url = "https://www.wikidata.org/w/rest.php/wikibase"
        self.headers = {'User-Agent': UA, 'Accept': 'application/json'}

    def search(self, q, lang="pl", limit=20, offset=0):
        url = self.base_url + "/v1/search/items"
        return f"{url}?{urllib.parse.urlencode({'q': q, 'language': lang, 'limit': limit, 'offset': offset})}"

    def make_request(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error("Wikidata API request failed: %s", e)
            return None
