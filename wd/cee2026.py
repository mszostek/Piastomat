import csv
import logging
from time import sleep

from lib.queries import query_qlever, query_wikidata

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

plain_countries = ["wd:Q222", "wd:Q399"]
properties = ["wdt:P17", "wdt:P27"]

# countries = [
#     {"name": "Kazachstan",             "country": "wd:Q232",    "local_wikis": ["<https://kk.wikipedia.org/>"]},
#     {"name": "Azerbejdżan",            "country": "wd:Q227",    "local_wikis": ["<https://az.wikipedia.org/>"]},
#                  ]
countries = [
    # {"name":"", "country":"", "local_wikis":"",},
    # {"name": "Albania",                "country": "wd:Q222",    "local_wikis": ["<https://sq.wikipedia.org/>"]},
    # {"name": "Armenia",                "country": "wd:Q399",    "local_wikis": ["<https://hy.wikipedia.org/>", "<https://hyw.wikipedia.org/>"]},
    # {"name": "j. arumuński",                "country": "wd:Q201111", "local_wikis": ["<https://roa-rup.wikipedia.org/>"]},
    # {"name": "Austria",                "country": "wd:Q40",     "local_wikis": ["<https://de.wikipedia.org/>"]},
    # {"name": "Azerbejdżan",            "country": "wd:Q227",    "local_wikis": ["<https://az.wikipedia.org/>"]},
    # {"name": "Baszkortostan",          "country": "wd:Q5710",   "local_wikis": ["<https://ba.wikipedia.org/>"]},
    # {"name": "Białoruś",               "country": "wd:Q184",    "local_wikis": ["<https://be.wikipedia.org/>", "<https://be-tarask.wikipedia.org/>"]},
    # {"name": "Bośnia i Hercegowina",   "country": "wd:Q225",    "local_wikis": ["<https://bs.wikipedia.org/>"]},
    # {"name": "Bułgaria",   "country": "wd:Q219",    "local_wikis": ["<https://bg.wikipedia.org/>"]},
    # {"name": "Czuwaszja",              "country": "wd:Q5466",   "local_wikis": ["<https://cv.wikipedia.org/>"]},
    # {"name": "Półwysep Krymski",   "country": "wd:Q7835",    "local_wikis": []},
    # {"name": "Karaimi",              "country": "wd:Q36",   "local_wikis": []},
    # {"name": "Tatarzy krymscy",        "country": "wd:Q117458", "local_wikis": ["<https://crh.wikipedia.org/>"]},
    # {"name": "Chorwacja",              "country": "wd:Q224",    "local_wikis": ["<https://hr.wikipedia.org/>"]},
    # {"name": "Czechy",              "country": "wd:Q213",    "local_wikis": ["<https://cs.wikipedia.org/>"]},
    # {"name": "Estonia",              "country": "wd:Q191",    "local_wikis": ["<https://et.wikipedia.org/>"]},
    # {"name": "Grecja",                 "country": "wd:Q41",     "local_wikis": ["<https://el.wikipedia.org/>"]},
    # {"name": "Węgry",                  "country": "wd:Q28",     "local_wikis": ["<https://hu.wikipedia.org/>"]},
    # {"name": "Iran",                  "country": "wd:Q794",     "local_wikis": ["<https://fa.wikipedia.org/>"]},
    # {"name": "Kazachstan",             "country": "wd:Q232",    "local_wikis": ["<https://kk.wikipedia.org/>"]},
    # {"name": "Kosowo",                 "country": "wd:Q1246",   "local_wikis": ["<https://sq.wikipedia.org/>"]},
    # {"name": "Krymczacy",                 "country": "wd:Q36",   "local_wikis": []},
    # {"name": "Łotwa",                  "country": "wd:Q211",    "local_wikis": ["<https://lv.wikipedia.org/>"]},
    # {"name": "Litwa",                  "country": "wd:Q37",     "local_wikis": ["<https://lt.wikipedia.org/>"]},
    # {"name": "Malta",                  "country": "wd:Q233",    "local_wikis": ["<https://mt.wikipedia.org/>"]},
    # {"name": "Czarnogóra",     "country": "wd:Q236",    "local_wikis": []},
    # {"name": "Macedonia Północna",     "country": "wd:Q221",    "local_wikis": ["<https://mk.wikipedia.org/>"]},
    # {"name": "Ruś Nowogrodzka",        "country": "wd:Q9324216","local_wikis": []},
    # {"name": "Republika Serbska",      "country": "wd:Q11196",    "local_wikis": ["<https://sr.wikipedia.org/>"]},
    # {"name": "Rumunia i Mołdawia",     "country": "wd:Q218",    "local_wikis": ["<https://ro.wikipedia.org/>"]},
    # {"name": "Romowie",                  "country": "wd:Q8060",    "local_wikis": ["<https://rmy.wikipedia.org/>"]},
    # {"name": "Rosja",                  "country": "wd:Q159",    "local_wikis": ["<https://ru.wikipedia.org/>"]},
    # {"name": "Serbia",                 "country": "wd:Q403",    "local_wikis": ["<https://sr.wikipedia.org/>"]},
    # {"name": "Słowacja",               "country": "wd:Q214",    "local_wikis": ["<https://sk.wikipedia.org/>"]},
    # {"name": "Słowenia",               "country": "wd:Q215",    "local_wikis": ["<https://sl.wikipedia.org/>"]},
    # {"name": "Języki łużyckie",       "country": "wd:Q146521",    "local_wikis": []},
    # {"name": "Tatarzy", "country": "wd:Q35565", "local_wikis": ["<https://tt.wikipedia.org/>"]},
    # {"name": "Turcja", "country": "wd:Q43", "local_wikis": ["<https://tr.wikipedia.org/>"]},
    # {"name": "Ukraina",                "country": "wd:Q212",    "local_wikis": ["<https://uk.wikipedia.org/>"]},
    # {"name": "Võro",                "country": "wd:Q188076",    "local_wikis": ["<https://fiu-vro.wikipedia.org/>"]},
    # {"name": "J. zachodnioormiański",     "country": "wd:Q36",    "local_wikis": ["<https://hyw.wikipedia.org/>"]},
    # {"name": "Gruzja",                 "country": "wd:Q230",    "local_wikis": ["<https://ka.wikipedia.org/>"]},
    # {"name": "Kirgistan",                 "country": "wd:Q813",    "local_wikis": ["<https://ky.wikipedia.org/>"]},
    # {"name": "Maroko",                 "country": "wd:Q1028",    "local_wikis": ["<https://ar.wikipedia.org/>"]},
    # {"name": "Jakucja",                 "country": "wd:Q6605",    "local_wikis": ["<https://sah.wikipedia.org/>"]},
    # {"name": "Tadżykistan",                 "country": "wd:Q863",    "local_wikis": ["<https://tg.wikipedia.org/>"]},
    # {"name": "Uzbekistan",                 "country": "wd:Q265",    "local_wikis": ["<https://uz.wikipedia.org/>"]},

    {"name": "Republika Dońska", "country": "wd:Q2453974", "local_wikis": ["<https://uk.wikipedia.org/>", "<https://ru.wikipedia.org/>"], },
    # {"name":"Polska", "country": "wd:Q36", "local_wikis":["<https://pl.wikipedia.org/>"], },
    # {"name":"Cypr", "country": "wd:Q229", "local_wikis":["<https://el.wikipedia.org/>"], },
    # {"name":"Erzianie", "country": "wd:Q47246", "local_wikis":["<https://myv.wikipedia.org/>"], },
    # {"name":"Esperanto", "country": "wd:Q143", "local_wikis":["<https://eo.wikipedia.org/>"], },
]

articles_query = '''
PREFIX schema: <http://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT DISTINCT (COUNT(*) AS ?arts) {{
  VALUES ?country {{ {country_values} }}
  VALUES ?props {{wdt:P17 wdt:P27}}
  ?article_pl schema:about ?item;
              schema:isPartOf {ispartof} .
  ?item ?prop ?country.
}}
'''

# SAMPLE, because Latvia has two areas
countries_query = '''
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT DISTINCT ?country (SAMPLE(?are) AS ?area) ?population {
VALUES ?country {wd:Q222 wd:Q399 wd:Q201111 wd:Q40 wd:Q227 wd:Q5710 wd:Q184 wd:Q225 wd:Q219 wd:Q5466 wd:Q7835 wd:Q36  wd:Q117458 wd:Q224 wd:Q213 wd:Q191 wd:Q41 wd:Q28 wd:Q794 wd:Q232 wd:Q1246 wd:Q36 wd:Q211 wd:Q37 wd:Q233 wd:Q236 wd:Q221 wd:Q9324216 wd:Q11196 wd:Q218 wd:Q36 wd:Q159 wd:Q403 wd:Q214 wd:Q215 wd:Q146521 wd:Q35565 wd:Q43 wd:Q212 wd:Q188076  wd:Q36 wd:Q230 wd:Q813 wd:Q1028 wd:Q6605 wd:Q863 wd:Q265 wd:Q36
wd:Q229 wd:Q47246 wd:Q143 wd:Q2453974
 }

  ?country wdt:P2046 ?are;
           wdt:P1082 ?population.
  } GROUP BY ?country ?population
'''

country_results = query_qlever(countries_query)
country_data = {}
for country in country_results['results']['bindings']:
    key = "wd:" + country['country']['value'][31:]
    country_data[key] = {
        'population': country['population']['value'],
        'area': country['area']['value']
    }

results = []
for country in countries:
    log.info("%s", country["name"])
    row = {'name': country["name"]}
    try:
        row['population'] = country_data[country['country']]['population']
        row['area'] = country_data[country['country']]['area']
    except KeyError:
        row['population'] = None
        row['area'] = None

    pl_wiki = query_qlever(articles_query.format(
        country_values=country["country"],
        ispartof="<https://pl.wikipedia.org/>"))
    try:
        row['pl_wiki'] = pl_wiki['results']['bindings'][0]['arts']['value']
    except (KeyError, IndexError, TypeError):
        row['pl_wiki'] = None
    sleep(.2)

    en_wiki = query_qlever(articles_query.format(
        country_values=country["country"],
        ispartof="<https://en.wikipedia.org/>"))
    try:
        row['en_wiki'] = en_wiki['results']['bindings'][0]['arts']['value']
    except (KeyError, IndexError, TypeError):
        row['en_wiki'] = None
    sleep(.2)

    row['local_wikis'] = 0
    if country['name'] != 'Polska' or len(country["local_wikis"]) >= 1:
        for local_wp in country["local_wikis"]:
            local_wiki = query_wikidata(articles_query.format(
                country_values=country["country"],
                ispartof=local_wp))
        try:
            row['local_wikis'] += int(local_wiki['results']['bindings'][0]['arts']['value'])
        except (KeyError, IndexError, TypeError):
            pass
        sleep(.2)

    results.append(row)
    with open('output/cee2026_2.tsv', 'w', newline='\n') as tsvfile:
        writer = csv.writer(tsvfile)
        writer.writerow(["Country", "Population", "Area (Km^2)", "Plwiki", "Enwiki", "LocalWiki"])
        writer.writerows([[r['name'], r['population'], r['area'], r['pl_wiki'], r['en_wiki'], r['local_wikis']] for r in results])
# Republika Dońska,,,38,40,52
