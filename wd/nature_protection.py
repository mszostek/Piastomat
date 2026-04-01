import logging

import mwparserfromhell
import pywikibot

from lib.site import get_site

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

site = get_site()

och_inbx = pywikibot.Page(site, "Szablon:Obszar chroniony infobox")
referring_pages = och_inbx.getReferences(only_template_inclusion=True, namespaces=[0])

OCH_NAMES = ['obszar chroniony infobox', 'szablon:obszar chroniony infobox']

iterator = 0
for page in referring_pages:
    log.info("%s", page.title())
    if iterator > 10:
        break
    iterator += 1

    try:
        wikicode = mwparserfromhell.parse(page.text)
        for template in wikicode.filter_templates():
            if str(template.name).strip().lower() in OCH_NAMES:
                for param in template.params:
                    if param.name in ['powierzchnia', 'powierzchnia otuliny']:
                        log.info("  %s: %s", param.name, param.value)
                    else:
                        log.info("  %s", param.name)
    except Exception as e:
        log.warning("Błąd przy %s: %s", page.title(), e)
        continue
