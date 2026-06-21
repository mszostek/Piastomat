#!/usr/bin/env python3
"""Zrzut treści wkładu wskazanych użytkowników (metadane + diff) do analizy.

Użycie:
    python dump_user_diffs.py Wandal1 "Inny Wandal" > output/user_investigate/zrzut.txt
    python dump_user_diffs.py            # użyje nazwy domyślnej poniżej

Treści nie ma w replikach Toolforge, więc lecimy przez Action API.
"""

import sys
import time
import difflib
import requests

API = "https://pl.wikipedia.org/w/api.php"
# Wikimedia wymaga sensownego User-Agent z kontaktem:
UA = "wandal-diff-dump/0.1 (https://pl.wikipedia.org/wiki/Wikipedysta:Piastomat)"
LIMIT = 50  # ile ostatnich edycji na użytkownika

S = requests.Session()
S.headers["User-Agent"] = UA


def get(**params):
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    params.setdefault("maxlag", "5")
    r = S.get(API, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def usercontribs(user, limit=LIMIT):
    out, cont = [], {}
    while len(out) < limit:
        data = get(action="query", list="usercontribs", ucuser=user,
                   uclimit=min(500, limit - len(out)),
                   ucprop="ids|title|timestamp|comment|sizediff|flags|tags",
                   **cont)
        out.extend(data["query"]["usercontribs"])
        cont = data.get("continue", {})
        if not cont:
            break
    return out[:limit]


def fetch_contents(revids):
    """Zwraca {revid: wikitekst}. Batch po 50 (limit revids w jednym zapytaniu)."""
    text = {}
    revids = [r for r in revids if r]  # parentid==0 => nowa strona, pomijamy
    for i in range(0, len(revids), 50):
        batch = revids[i:i + 50]
        data = get(action="query", prop="revisions",
                   revids="|".join(map(str, batch)),
                   rvprop="ids|content", rvslots="main")
        for page in data["query"].get("pages", []):
            for rev in page.get("revisions", []):
                text[rev["revid"]] = rev["slots"]["main"].get("content", "")
        time.sleep(0.1)
    return text


def unified(old, new, ctx=2):
    diff = difflib.unified_diff(old.splitlines(), new.splitlines(),
                                lineterm="", n=ctx)
    return "\n".join(l for l in diff if not l.startswith(("---", "+++")))


def dump(user, limit=LIMIT):
    contribs = usercontribs(user, limit)
    need = set()
    for c in contribs:
        need.add(c["revid"])
        if c.get("parentid"):
            need.add(c["parentid"])
    text = fetch_contents(sorted(need))

    print(f"===== {user} ({len(contribs)} edycji) =====\n")
    for c in contribs:
        old = text.get(c.get("parentid") or 0, "")
        new = text.get(c["revid"], "")
        flags = []
        if "new" in c:
            flags.append("NOWA STRONA")
        if "minor" in c:
            flags.append("drobna")
        if c.get("tags"):
            flags.append("tagi: " + ", ".join(c["tags"]))
        print(f"--- [{c['timestamp']}] {c['title']} (Δ{c['sizediff']:+d}) "
              f"{' | '.join(flags)}")
        print(f"    oldid={c['revid']}  opis: {c.get('comment') or '(brak)'}")
        d = unified(old, new)
        print(d if d.strip() else "    (brak zmian w samej treści — np. przeniesienie/usunięcie?)")
        print()


if __name__ == "__main__":
    users = sys.argv[1:] or ["Przyklad_wandal"]
    for u in users:
        dump(u)
        print("\n")
