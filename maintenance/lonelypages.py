import pywikibot

CATEGORY = 'Kategoria:Łódź'

site = pywikibot.Site('pl', 'wikipedia')
cat = pywikibot.Category(site, CATEGORY)

lonely_set = {page.title() for page in site.querypage('Lonelypages')}

index = 1
print(CATEGORY)
# list(cat.articles(recurse=True))
for page in cat.articles(recurse=True, namespaces=0):
    if page.title() in lonely_set:
        print(f"# [[{page.title()}]]")
        index += 1
