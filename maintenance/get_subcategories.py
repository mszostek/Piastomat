
import pywikibot

from lib.categories import subcategories_with_path, category_prefixes

# PARENT = "GLAM in Poland"
PARENT = "Photographs by Hans-Peter Bärtschi"

def main():

    site = pywikibot.Site('commons')
    site.login()

    cat = pywikibot.Category(site, f'{site.namespace(14)}:{PARENT}')

    for subcat, path in subcategories_with_path(cat):
        print(' > '.join(c.title(without_brackets=True) for c in path))
        # print(']] > [[:'.join(c.title(without_brackets=True) for c in path))

if __name__ == '__main__':
    main()