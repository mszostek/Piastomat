import pywikibot

site = pywikibot.Site()
site.login()
wikidata = site.data_repository()

nft_template = pywikibot.Page(site, 'Szablon:NFT')