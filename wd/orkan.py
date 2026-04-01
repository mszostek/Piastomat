import logging

import pywikibot

from lib.site import get_site, get_wikidata

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

data = {
    "2002": ["Józef Baran (poeta)", "Henryk Cyganik", "Julian Kawalec", "Mikołaj Samojlik"],
    "2003": ["Stanisław Baj", "Henryk Bereza", "Zbigniew Dmitroca"],
    "2004": ["Jacek Lubart-Krzysica", "Rafał Wojasiński", "Tadeusz Górny"],
    "2005": ["Witold Knychalski", "Jan Fudala", "Wacław Kostrzewa"],
    "2006": ["Andrzej Grabowski (poeta)", "Stanisław Hodorowicz", "Stanisław Pasoń"],
    "2007": ["Adam Ziemianin", "Wanda Czubernat", "Anna Łękawa"],
    "2008": ["Marian Ormaniec", ],
    "2009": ["Barbara Krężołek-Paluch", "Waleria Prochownik", "Rafał Skąpski", "Jerzy Skrobot", "Franciszek Stefaniuk", "Juliusz Wątroba"],
    "2011": ["Tadeusz Trębacz", "Zbigniew Masternak"],
    "2012": ["Jan Sęk"],
    "2013": ["Bernard Ładysz", "Lucyna Kozłowska", "Andrzej Kozłowski (rzeźbiarz)", "Marian Pilot"],
    "2014": ["Jerzy Hoffman", "Uniwersytet ludowy w Radawnicy"],
    "2018": ["Janusz Gmitruk" ,"Henryk Kozubski"],
    "2024": ["Kamila Lićwinko", "Olgierd Łukaszewicz"],
}

site = get_site()
wikidata = get_wikidata(site)

property_award = "P166"
item_orkan = "Q138493864"
property_date = "P585"
property_source = "S143"
item_plwiki = "Q1551807"
property_sources_access = "S813"
source_accessed = "+2026-02-26T00:00:00Z/11"

for year, people in data.items():
    for awarded in people:
        page = pywikibot.Page(site, awarded)
        try:
            wikidata_item = pywikibot.ItemPage.fromPage(page)
            print(f"{wikidata_item.title()}\t{property_award}\t{item_orkan}\t{property_date}\t+{year}-01-01T00:00:00Z/09\t{property_source}\t{item_plwiki}\t{property_sources_access}\t{source_accessed}")
        except pywikibot.exceptions.NoPageError:
            log.warning("Brak elementu Wikidanych: %s", awarded)
