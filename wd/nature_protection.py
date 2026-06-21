import csv
import logging
import locale
import mwparserfromhell
import pywikibot

from lib.site import get_site

locale.setlocale(locale.LC_ALL, '')

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

site = get_site()

och_infobox = pywikibot.Page(site, "Szablon:Obszar chroniony infobox")
referring_pages = och_infobox.getReferences(only_template_inclusion=True, namespaces=[0])

OCH_NAMES = ['obszar chroniony infobox', 'szablon:obszar chroniony infobox']

iterator = 0
results, noresults = [], []
for page in referring_pages:
    log.info("%s", page.title())
    # if iterator > 10:
    #     break
    # iterator += 1

    try:
        wikidata_item = pywikibot.ItemPage.fromPage(page)
        row = {'name': wikidata_item.title(), 'wd': page.title()}
        wikicode = mwparserfromhell.parse(page.text)
        for template in wikicode.filter_templates():
            if str(template.name).strip().lower() in OCH_NAMES:
                for param in template.params:
                    if param.name.strip() in ['powierzchnia', 'powierzchnia otuliny']:
                        if param.value.strip() != '':
                            value, unit = param.value.strip().rsplit(' ', maxsplit=1)
                            if param.name.strip() == 'powierzchnia':
                                row['P2046'] = value
                                row['P2046_unit'] = unit
                            else:
                                row['P2046_2'] = value
                                row['P2046_2_unit'] = unit
                if len(row) > 2:
                    results.append(row)
                else:
                    noresults.append(row)

    except Exception as e:
        log.warning("Błąd przy %s: %s", page.title(), e)
        continue

with open('output/nature_reserves_data.tsv', 'w', newline='\n') as tsvfile:
    writer = csv.writer(tsvfile, delimiter="\t")
    writer.writerow(["WD", "Title", "Area", "Area unit", "Additional area", "Additional unit"])
    writer.writerows([[r['name'], r['wd'], r.get('P2046'), r.get('P2046_unit'), r.get('P2046_2'), r.get('P2046_2_unit')] for r in results])
with open('output/nature_reserves_nodata.tsv', 'w', newline='\n') as tsvfile:
    writer = csv.writer(tsvfile, delimiter="\t")
    writer.writerow(["WD", "Title", "Area", "Area unit", "Additional area", "Additional unit"])
    writer.writerows([[r['name'], r['wd'], r.get('P2046'), r.get('P2046_unit'), r.get('P2046_2'), r.get('P2046_2_unit')] for r in noresults])
