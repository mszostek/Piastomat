#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ujednolicenie sortowania kategorii krajowych w
[[Kategoria:Kategorie według miejscowości]].

maintance/sort_kategorie_wg_miejscowości.py #dry run
maintance/sort_kategorie_wg_miejscowości.py --save
"""

import argparse

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators

from lib.categories import category_name, category_prefixes

PARENT = 'Kategorie według miejscowości'        # bez prefiksu przestrzeni nazw
SUMMARY = ('sortowanie kategorii krajowej pod nazwą państwa w mianowniku '
           '(zamiast wykrzyknika)')


def sortkey(link):
    return None if link.text is None else str(link.text)


def find_country(code, prefixes, parent_name):
    """Nazwa państwa = kategoria eponimiczna na stronie.

    Preferowana: jedyna kategoria sortowana pod spacją/pustym kluczem.
    Awaryjnie: jedyna kategoria różna od nadrzędnej, gdy nie ma takiej
    pod spacją. W przeciwnym razie None (przypadek do ręcznego sprawdzenia).
    """
    non_parent, blank = [], []
    for link in code.filter_wikilinks():
        name = category_name(link, prefixes)
        if name is None or name == parent_name:
            continue
        non_parent.append(name)
        sk = sortkey(link)
        if sk is not None and sk.strip() == '':
            blank.append(name)

    if len(blank) == 1:
        return blank[0]
    if not blank and len(non_parent) == 1:
        return non_parent[0]
    return None


def fixed_text(page, prefixes, parent_name):
    """Zwraca poprawiony wikitekst albo None, jeśli nie ma czego zmieniać."""
    code = mwparserfromhell.parse(page.text)

    parent_link = next(
        (l for l in code.filter_wikilinks()
         if category_name(l, prefixes) == parent_name),
        None,
    )
    if parent_link is None:
        return None  # brak kategorii nadrzędnej (nie powinno wystąpić)

    sk = sortkey(parent_link)
    if sk is None or not sk.strip().startswith('!'):
        return None  # nie jest sortowana pod wykrzyknikiem

    country = find_country(code, prefixes, parent_name)
    if country is None:
        pywikibot.warning(
            f'{page.title()}: nie ustalono jednoznacznie państwa '
            f'(klucz "{sk}") – pomijam')
        return None

    parent_link.text = country
    new_text = str(code)
    return new_text if new_text != page.text else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save', action='store_true',
                        help='zapisuj zmiany (domyślnie tryb próbny)')
    args = parser.parse_args()

    site = pywikibot.Site('pl', 'wikipedia')
    site.login()
    prefixes = category_prefixes(site)
    parent_name = ' '.join(PARENT.split())

    cat = pywikibot.Category(site, f'{site.namespace(14)}:{PARENT}')
    gen = pagegenerators.PreloadingGenerator(
        cat.subcategories(recurse=False), groupsize=100)

    changed = skipped = saved = 0
    for page in gen:
        new_text = fixed_text(page, prefixes, parent_name)
        if new_text is None:
            skipped += 1
            continue

        changed += 1
        pywikibot.output(f'\n=== {page.title()} ===')
        pywikibot.showDiff(page.text, new_text)

        if not args.save:
            continue

        page.text = new_text
        try:
            page.save(summary=SUMMARY, minor=True)
            saved += 1
        except pywikibot.exceptions.Error as exc:
            pywikibot.error(f'{page.title()}: {exc}')

    pywikibot.output(
        f'\nKoniec. Do zmiany: {changed}, pominięto: {skipped}, '
        f'zapisano: {saved}'
        + ('' if args.save else ' (tryb próbny – uruchom z --save)'))


if __name__ == '__main__':
    main()
