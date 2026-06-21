#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_chemia_info.py

Dodaje szablon {{Wikiprojekt:Chemia/info}} na początek stron dyskusji
artykułów należących do [[Kategoria:Chemicy]].

Zasady:
  * jeśli szablon już występuje na stronie dyskusji -> pomijamy (bez dubli),
  * jeśli strona dyskusji nie istnieje          -> tworzymy ją z samym szablonem,
  * jeśli istnieje                              -> wstawiamy szablon na samą górę.

Rozpoznawanie szablonu jest odporne na warianty zapisu (małe/wielkie litery
w prefiksie przestrzeni nazw, podkreślenia vs spacje, dodatkowe parametry)
dzięki porównaniu znormalizowanych tytułów (pywikibot) + parsowaniu
mwparserfromhell. NIE wykrywa natomiast przekierowań-aliasów szablonu
(gdyby ktoś transkludował np. {{WP Chemia}} -> Wikiprojekt:Chemia/info).

Globalne argumenty pywikibota działają normalnie, m.in.:
    python add_chemia_info.py -simulate   # przebieg na sucho, bez zapisu
    python add_chemia_info.py -log
"""

import pywikibot
from pywikibot import pagegenerators
import mwparserfromhell

CATEGORY = 'Chemicy'
TEMPLATE_TITLE = 'Wikiprojekt:Chemia/info'          # kanoniczny tytuł transkluzji
TEMPLATE_TEXT = '{{Wikiprojekt:Chemia/info}}'
SUMMARY = 'dodanie szablonu {{Wikiprojekt:Chemia/info}}'
RECURSE = True   # True -> wejdź również w podkategorie Kategorii:Chemicy


def has_template(text, target_title, site):
    """Czy w tekście jest już transkluzja docelowego szablonu?"""
    if not text:
        return False
    for tpl in mwparserfromhell.parse(text).filter_templates():
        name = str(tpl.name).strip()
        try:
            if pywikibot.Page(site, name).title() == target_title:
                return True
        except (ValueError, pywikibot.exceptions.Error):
            # nazwa nie jest poprawnym tytułem (np. funkcja parsera) -> pomijamy
            continue
    return False


def main():
    pywikibot.handle_args()  # obsługa globalnych argumentów (-simulate, -log, ...)
    site = pywikibot.Site('pl', 'wikipedia')
    site.login()

    target_title = pywikibot.Page(site, TEMPLATE_TITLE).title()

    cat = pywikibot.Category(site, CATEGORY)
    articles = list(cat.articles(namespaces=[0], recurse=RECURSE))
    talks = [a.toggleTalkPage() for a in articles]

    pywikibot.output(
        f'Artykułów w [[Kategoria:{CATEGORY}]]: {len(articles)} (recurse={RECURSE})'
    )

    added = skipped = errors = 0

    for talk in pagegenerators.PreloadingGenerator(talks):
        try:
            text = talk.text if talk.exists() else ''

            if has_template(text, target_title, site):
                pywikibot.output(f'POMINIĘTO (już jest): {talk.title()}')
                skipped += 1
                continue

            talk.text = TEMPLATE_TEXT + '\n' + text
            talk.save(summary=SUMMARY, minor=False, botflag=True)
            added += 1

        except pywikibot.exceptions.Error as e:
            pywikibot.error(f'Błąd przy {talk.title()}: {e}')
            errors += 1

    pywikibot.output(
        f'\nGotowe. Dodano: {added}, pominięto: {skipped}, błędów: {errors}.'
    )


if __name__ == '__main__':
    main()
