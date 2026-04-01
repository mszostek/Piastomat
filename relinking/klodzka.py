import difflib
import logging

import pywikibot
from pywikibot import pagegenerators

from lib.site import get_site

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

site = get_site()

DRY_RUN = False

old_url = "https://www.pwnhc.ca/download/gazetteer-of-the-northwest-territories/?wpdmdl=3032"
new_url = "https://www.ece.gov.nt.ca/sites/ece/files/resources/nwt_gazetteer_2017_0.pdf"

search_query = r'insource:"https://www.pwnhc.ca/download/gazetteer-of-the-northwest-territories/?wpdmdl=3032"'

gen = pagegenerators.SearchPageGenerator(search_query, site=site, namespaces=[0])

for iterator, page in enumerate(gen, start=1):
    old_text = page.text
    new_text = old_text.replace(old_url, new_url)

    if old_text == new_text:
        log.info("%d. %s — brak zmian", iterator, page.title())
        continue

    log.info("%d. %s", iterator, page.title())

    if DRY_RUN:
        diff = difflib.unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=page.title(),
            tofile=page.title(),
        )
        print("".join(diff))
    else:
        page.text = new_text
        page.save(
            summary="Zmiana linku: pwnhc.ca → ece.gov.nt.ca",
            minor=True
        )
