import pywikibot


def category_prefixes(site):
    """Wszystkie lokalne nazwy przestrzeni Kategoria: (np. kategoria, category)."""
    ns = site.namespaces[14]
    names = {ns.canonical_name, ns.custom_name, *ns.aliases}
    return {n.lower() for n in names if n}


def category_name(link, prefixes):
    """Znormalizowana nazwa kategorii z linku (bez prefiksu) albo None."""
    title = str(link.title)
    if ':' not in title:
        return None
    prefix, _, rest = title.partition(':')
    if prefix.strip().lower() not in prefixes:
        return None
    name = ' '.join(rest.replace('_', ' ').split())
    return name[:1].upper() + name[1:] if name else name


def subcategories_with_path(cat, path=None, recursed=None):
    if path is None:
        path = [cat]
    if recursed is None:
        recursed = set()
    if cat.title() in recursed:
        return
    recursed.add(cat.title())
    for subcat in cat.subcategories():
        current_path = path + [subcat]
        yield subcat, current_path
        yield from subcategories_with_path(subcat, current_path, recursed)
