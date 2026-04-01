import pywikibot


def get_site():
    site = pywikibot.Site()
    site.login()
    return site


def get_wikidata(site):
    return site.data_repository()
