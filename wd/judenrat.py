import time

import mwparserfromhell
import pywikibot

from lib.queries import WikidataAPI
from lib.site import get_site

site = get_site()

page = pywikibot.Page(site, "Judenrat w Łodzi")
wikicode = mwparserfromhell.parse(page.text)

link_interwiki_templates = wikicode.filter_templates(matches='link-interwiki')
interwikis = {}
for template in link_interwiki_templates:
    params = {str(p.name).strip(): str(p.value).strip() for p in template.params}
    interwikis[params['1']] = params['Q']

red_links = []
for linked in page.linkedPages(follow_redirects=True):
    if not linked.exists():
        current_link = {"title": linked.title()}
        if linked.title() in interwikis:
            current_link["interwiki"] = interwikis[linked.title()]
        red_links.append(current_link)

wikidata_api = WikidataAPI()
for link in red_links:
    if "interwiki" not in link.keys():
        search_url = wikidata_api.search(link["title"], limit=5)
        results = wikidata_api.make_request(search_url)
        print(f"# [[{link['title']}]] – [{search_url} link]")
        if results and len(results["results"]) > 0:
            for result in results["results"]:
                print(f"## [[:d:{result['id']}|{result['id']}]] {{{{s|link-interwiki|{result['id']}|{link['title']}}}}} (match: {result['match']['text']} ({result['match']['language']} {result['match']['type']}) – "
                      f"{(result.get('display-label') or {}).get('value')}, {(result.get('description') or {}).get('value')}")
        time.sleep(.5)
