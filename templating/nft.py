"""
NFT template synchronization and verification.

Functions:
  sync_players()     – aktualizuj NFT|p w Wikipedii na podstawie P2574 w Wikidanych
                       (dawne nft_edits.py)
  sync_non_players() – aktualizuj NFT|k/t/... w Wikipedii; brakujące wartości zapisz do CSV
                       (dawne nft_not_players.py)
  verify_players()   – weryfikuj NFT|p przez zapytanie SPARQL do Wikidanych
                       (dawne nft_players_verification.py)
  verify_multiple()  – sprawdź spójność stron z wieloma szablonami NFT
                       (dawne nft_verification_multiple_calls.py)
  test_headings()    – eksploracyjnie wyciągnij nagłówki ze stron bez szablonu NFT
                       (dawne nft_testing.py)
"""

import csv
import logging

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators

from lib.queries import query_wikidata
from lib.site import get_site
from lib.streditor import remove_parenthetical

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

NFT_NAMES = ['nft', 'szablon:nft']


# ---------------------------------------------------------------------------
# sync_players
# ---------------------------------------------------------------------------

def sync_players(dry_run=True, skip=0):
    """
    Przeiteruj przez wszystkie strony używające szablonu NFT|p i zaktualizuj
    drugi parametr (numer NFT) na podstawie wartości P2574 w Wikidanych.

    Parametr `skip` pozwala wznowić od danego miejsca (np. skip=9880 aby
    pominąć pierwsze 9880 stron).
    """
    site = get_site()

    nft_template = pywikibot.Page(site, 'Szablon:NFT')
    referring_pages = nft_template.getReferences(only_template_inclusion=True, namespaces=[0])

    iterator = 0
    for page in referring_pages:
        iterator += 1
        if iterator <= skip:
            continue

        try:
            wikicode = mwparserfromhell.parse(page.text)
            for template in wikicode.filter_templates():
                if str(template.name).strip().lower() not in NFT_NAMES:
                    continue
                params = template.params
                if len(params) < 2:
                    continue
                if params[0].value != "p":
                    continue

                second_param = str(params[1].value).strip()

                try:
                    wikidata_item = pywikibot.ItemPage.fromPage(page)
                    item_dict = wikidata_item.get()
                    p2574_value = None
                    if 'P2574' in item_dict['claims']:
                        p2574_value = item_dict['claims']['P2574'][0].getTarget()

                    if p2574_value is None or second_param == p2574_value:
                        log.info("%d – %s: bez zmian (NFT=%s, P2574=%s)", iterator, page.title(), second_param, p2574_value)
                        continue

                    params[1].value = str(p2574_value)
                    if "(" in page.title():
                        template.add(3, value=remove_parenthetical(page.title()))

                    if dry_run:
                        log.info("[DRY RUN] %s: %s → %s", page.title(), second_param, p2574_value)
                    else:
                        page.text = str(wikicode)
                        page.save(
                            summary=f"Aktualizacja parametru NFT za WD ({second_param} → {p2574_value})",
                            minor=True
                        )
                        log.info("Zapisano: %s (%s → %s)", page.title(), second_param, p2574_value)

                except pywikibot.exceptions.NoPageError:
                    log.warning("%s: brak elementu Wikidanych (NFT=%s)", page.title(), second_param)

        except Exception as e:
            log.error("Błąd przy %s: %s", page.title(), e)


# ---------------------------------------------------------------------------
# sync_non_players
# ---------------------------------------------------------------------------

def sync_non_players(dry_run=True):
    """
    Dla szablonów NFT z pierwszym parametrem innym niż 'p' (np. 'k' – klub,
    't' – trener) zaktualizuj drugi parametr na podstawie właściwości Wikidanych.
    Elementy bez tej właściwości w WD zbierz do CSV.

    Mapowanie litera → właściwość WD:
      k → P8147  (klub)
      t → P10995 (trener)
    """
    site = get_site()

    wd_property = {
        'k': 'P8147',   # klub/club
        't': 'P10995',  # trener/coach
    }
    wd_results = []

    for letter, prop in wd_property.items():
        search_query = r'insource:"{{NFT\|' + letter + r'"i'
        gen = pagegenerators.SearchPageGenerator(search_query, site=site, namespaces=[0])
        iterator = 0

        for page in gen:
            iterator += 1
            log.info("%d. %s: %s", iterator, letter, page.title())

            try:
                wikicode = mwparserfromhell.parse(page.text)
                for template in wikicode.filter_templates():
                    if str(template.name).strip().lower() not in NFT_NAMES:
                        continue
                    params = template.params
                    if len(params) < 2:
                        continue
                    if params[0].value == "p":
                        continue

                    second_param = str(params[1].value).strip()

                    try:
                        wikidata_item = pywikibot.ItemPage.fromPage(page)
                        item_dict = wikidata_item.get()
                        wd_prop_value = None
                        if prop in item_dict['claims']:
                            wd_prop_value = item_dict['claims'][prop][0].getTarget()
                        else:
                            wd_results.append({
                                'wd_item': wikidata_item.id,
                                'property': prop,
                                'value': second_param,
                                'source': "S143",
                                'plwiki': "Q1551807",
                                'stime': "S813",
                                'time': "+2026-02-22T00:00:00Z/11",
                            })

                        if wd_prop_value is None or second_param == wd_prop_value:
                            log.info("%s: bez zmian (%s=%s)", page.title(), prop, wd_prop_value)
                            continue

                        params[1].value = str(wd_prop_value)
                        if "(" in page.title():
                            template.add(3, value=remove_parenthetical(page.title()))

                        if dry_run:
                            log.info("[DRY RUN] %s: %s → %s (%s)", page.title(), second_param, wd_prop_value, prop)
                        else:
                            page.text = str(wikicode)
                            page.save(
                                summary=f"Aktualizacja parametru NFT za WD ({second_param} → {wd_prop_value}, {prop})",
                                minor=True
                            )
                            log.info("Zapisano: %s (%s → %s)", page.title(), second_param, wd_prop_value)

                    except pywikibot.exceptions.NoPageError:
                        log.warning("%s: brak elementu Wikidanych (NFT=%s)", page.title(), second_param)

            except Exception as e:
                log.error("Błąd przy %s: %s", page.title(), e)

    with open('output/nft_P8147_P10995_to_WD.csv', 'w+', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['wd_item', 'property', 'value', 'source', 'plwiki', 'stime', 'time'])
        writer.writeheader()
        writer.writerows(wd_results)
    log.info("Zapisano %d wierszy do output/nft_P8147_P10995_to_WD.csv", len(wd_results))


# ---------------------------------------------------------------------------
# verify_players
# ---------------------------------------------------------------------------

def verify_players(dry_run=True):
    """
    Sprawdź wszystkie elementy Wikidanych z P2574 powiązane z polską Wikipedią.
    Kategoryzuje strony jako: brak szablonu, wiele szablonów, OK, do zmiany.
    Zapisuje wyniki do plików TSV w output/.
    """
    site = get_site()

    query = '''SELECT * {
      ?item wdt:P2574 ?nft.
      ?sitelink schema:about ?item;
                schema:isPartOf <https://pl.wikipedia.org/>;
                schema:name ?name.
    } ORDER BY ?name'''

    no_nft, multiple_nft, ok_nft, changed_nft, check_nft_type = [], [], [], [], []
    changed_nft.append(['title', 'old', 'new', 'link_title'])

    results = query_wikidata(query)
    for result in results["results"]["bindings"]:
        page = pywikibot.Page(site, result["name"]["value"])
        wikicode = mwparserfromhell.parse(page.text)
        templates = wikicode.filter_templates(matches='nft')

        if len(templates) == 0:
            no_nft.append([page.title(), result["item"]["value"], result["nft"]["value"]])
            continue
        if len(templates) > 1:
            multiple_nft.append([page.title(), result["item"]["value"]])
            continue

        params = templates[0].params
        if params[0].value != "p":
            check_nft_type.append([page.title(), result["item"]["value"], result["nft"]["value"]])
            continue

        second_param = str(params[1].value).strip()
        new_third_param = None
        try:
            params[2].value  # third param already exists
        except IndexError:
            title = result["name"]["value"]
            if title != remove_parenthetical(title):
                new_third_param = remove_parenthetical(title)

        if result["nft"]["value"] != second_param or new_third_param is not None:
            changed_nft.append([page.title(), second_param, result["nft"]["value"], new_third_param])
            params[1].value = result["nft"]["value"]
            if new_third_param is not None:
                templates[0].add(3, value=new_third_param)
            if dry_run:
                log.info("[DRY RUN] %s: %s → %s (param3=%s)", page.title(), second_param, result["nft"]["value"], new_third_param)
            else:
                page.text = str(wikicode)
                page.save(minor=True, summary="Aktualizacja szablonu NFT dla piłkarzy")
                log.info("Zapisano: %s: %s → %s", page.title(), second_param, result["nft"]["value"])
        else:
            ok_nft.append([page.title(), result["nft"]["value"], second_param])

    log.info("Wyniki: brak=%d, wiele=%d, ok=%d, zmienione=%d, do_sprawdzenia=%d",
             len(no_nft), len(multiple_nft), len(ok_nft), len(changed_nft) - 1, len(check_nft_type))

    with open("output/nft_verification_no_nft.tsv", "w") as f:
        csv.writer(f, delimiter="\t").writerows(no_nft)
    with open("output/nft_verification_multiple_nft.tsv", "w") as f:
        csv.writer(f, delimiter="\t").writerows(multiple_nft)
    with open("output/nft_verification_ok_nft.tsv", "w") as f:
        csv.writer(f, delimiter="\t").writerows(ok_nft)
    with open("output/nft_verification_changed_nft.tsv", "w") as f:
        csv.writer(f, delimiter="\t").writerows(changed_nft)
    with open("output/nft_verification_nft_type_to_check.tsv", "w") as f:
        csv.writer(f, delimiter="\t").writerows(check_nft_type)


# ---------------------------------------------------------------------------
# verify_multiple
# ---------------------------------------------------------------------------

def verify_multiple():
    """
    Sprawdź strony z wieloma szablonami NFT (plik wejściowy:
    output/nft_verification_multiple_nft.tsv) pod kątem spójności
    z wartością P2574 w Wikidanych. Wypisuje niezgodności.
    """
    site = get_site()

    with open("output/nft_verification_multiple_nft.tsv", "r") as f:
        tsv_reader = csv.DictReader(f, delimiter="\t")
        for i, line in enumerate(tsv_reader, start=1):
            page = pywikibot.Page(site, line["title"])
            wikicode = mwparserfromhell.parse(page.text)
            templates = wikicode.filter_templates(matches=u'nft\|p')

            try:
                for template in templates:
                    if template.name != "nft":
                        continue
                    wikidata_item = pywikibot.ItemPage.fromPage(page)
                    item_dict = wikidata_item.get()
                    p2574_value = None
                    if 'P2574' in item_dict['claims']:
                        p2574_value = item_dict['claims']['P2574'][0].getTarget()
                    if p2574_value is not None and template.params[1].value.strip() != p2574_value:
                        log.info("Do poprawy: %d. %s – %s", i, line['title'], line.get("wikidata", ""))
            except Exception as e:
                log.error("Błąd: %d. %s: %s", i, line['title'], e)


# ---------------------------------------------------------------------------
# test_headings
# ---------------------------------------------------------------------------

def test_headings(limit=5):
    """
    Eksploracyjnie wyciągnij nagłówki ze stron bez szablonu NFT
    (plik wejściowy: output/nft_verification_no_nft.tsv).
    """
    site = get_site()

    with open("output/nft_verification_no_nft.tsv", "r") as f:
        tsv_reader = csv.DictReader(f, delimiter="\t")
        for i, line in enumerate(tsv_reader, start=1):
            page = pywikibot.Page(site, line["title"])
            wikicode = mwparserfromhell.parse(page.text)
            headings = wikicode.filter_headings()
            log.info("%s: %s", page.title(), headings)
            if i >= limit:
                break


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Odkomentuj i uruchom wybraną funkcję:
    # sync_players(dry_run=True)
    # sync_non_players(dry_run=True)
    # verify_players(dry_run=True)
    # verify_multiple()
    # test_headings()
    pass
