import re


def remove_parenthetical(s):
    return re.sub(r'\s*\([^)]*\)$', '', s).strip()