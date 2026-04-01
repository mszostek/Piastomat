## Cell 3: Routes (lines) with stops, terminus (P559), and line number (P1671)

import logging

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

gtfs = "/home/maciek/Projects/wiki/wd/mpk_lodz/GTFS"

# --- Load data ---
routes = pd.read_csv(f"{gtfs}/routes.txt", encoding="utf-8-sig")
trips = pd.read_csv(f"{gtfs}/trips.txt", encoding="utf-8-sig",
                     usecols=["trip_id", "route_id", "direction_id"])
stops_gtfs = pd.read_csv(f"{gtfs}/stops.txt", encoding="utf-8-sig", dtype={"stop_code": str})
stops_gtfs["stop_code"] = stops_gtfs["stop_code"].str.strip()

# Wikidata stops (already created)
wd_stops = pd.read_csv("/home/maciek/Projects/wiki/wd/mpk_lodz/stops_on_wd.tsv", sep="\t")
wd_stops["stop_code"] = wd_stops["label"].str.extract(r'\((\d+)\)')
wd_stops["qid"] = wd_stops["item"].str.extract(r'(Q\d+)')
# Map stop_code -> Wikidata QID
code_to_qid = dict(zip(wd_stops["stop_code"].dropna(), wd_stops.loc[wd_stops["stop_code"].notna(), "qid"]))

# Map GTFS stop_id -> stop_code
id_to_code = dict(zip(stops_gtfs["stop_id"], stops_gtfs["stop_code"]))

# --- Build route -> ordered stops using chunked stop_times ---
# For each route, pick one representative trip per direction
# and collect stops in order
route_trips = {}
for _, trip in trips.iterrows():
    rid = trip["route_id"]
    did = trip["direction_id"]
    key = (rid, did)
    if key not in route_trips:
        route_trips[key] = trip["trip_id"]

# Collect all representative trip_ids
rep_trip_ids = set(route_trips.values())

# Read stop_times in chunks, filter to representative trips only
trip_stops = {}  # trip_id -> [(seq, stop_id), ...]
for chunk in pd.read_csv(f"{gtfs}/stop_times.txt", encoding="utf-8-sig",
                          usecols=["trip_id", "stop_id", "stop_sequence"],
                          chunksize=100000):
    mask = chunk["trip_id"].isin(rep_trip_ids)
    for _, row in chunk[mask].iterrows():
        trip_stops.setdefault(row["trip_id"], []).append(
            (row["stop_sequence"], row["stop_id"])
        )

# Sort by sequence
for tid in trip_stops:
    trip_stops[tid].sort()

# --- Build route -> all stops (unique) and terminus stops ---
route_all_stops = {}   # route_id -> set of stop_ids
route_terminus = {}    # route_id -> set of terminus stop_ids (first & last)

for (rid, did), tid in route_trips.items():
    if tid not in trip_stops:
        continue
    seq_stops = trip_stops[tid]
    stop_ids = [s[1] for s in seq_stops]

    route_all_stops.setdefault(rid, set()).update(stop_ids)

    # First and last are terminus
    first_stop = stop_ids[0]
    last_stop = stop_ids[-1]
    route_terminus.setdefault(rid, set()).add(first_stop)
    route_terminus.setdefault(rid, set()).add(last_stop)

# --- QuickStatements generation ---
source = '\tS854\t"https://otwarte.miasto.lodz.pl/transport_komunikacja/"\tS813\t+2026-03-29T00:00:00Z/11'

lines = []
stats = {"tram": 0, "bus": 0, "stops_linked": 0, "terminus_linked": 0}

for _, row in routes.iterrows():
    rid = row["route_id"]
    name = str(row["route_short_name"]).strip('"')
    is_tram = row["route_type"] == 0

    type_label = "tramwajowa" if is_tram else "autobusowa"
    p31 = "Q15145593" if is_tram else "Q3240003"
    stats["tram" if is_tram else "bus"] += 1

    label = f"linia {type_label} {name} w Łodzi"
    desc = f"linia {type_label} w aglomeracji łódzkiej"

    lines.append("CREATE")
    lines.append(f'LAST\tLpl\t"{label}"')
    lines.append(f'LAST\tDpl\t"{desc}"')
    lines.append(f'LAST\tP31\t{p31}{source}')
    lines.append(f'LAST\tP17\tQ36{source}')
    lines.append(f'LAST\tP131\tQ580{source}')
    lines.append(f'LAST\tP137\tQ11780295{source}')

    # P1671 - line number (official route designation)
    lines.append(f'LAST\tP1671\t"{name}"{source}')

    # P559 - terminus (first & last stops)
    terminus_ids = route_terminus.get(rid, set())
    for sid in terminus_ids:
        code = id_to_code.get(sid)
        if code and code in code_to_qid:
            qid = code_to_qid[code]
            lines.append(f'LAST\tP559\t{qid}{source}')
            stats["terminus_linked"] += 1

    # Stops served by this route (all stops from all directions)
    all_stop_ids = route_all_stops.get(rid, set())
    for sid in sorted(all_stop_ids):
        code = id_to_code.get(sid)
        if code and code in code_to_qid:
            qid = code_to_qid[code]
            # Skip if already added as terminus
            if sid not in terminus_ids:
                lines.append(f'LAST\tP527\t{qid}{source}')
            stats["stops_linked"] += 1

    lines.append("")

output = "\n".join(lines)

with open("/home/maciek/Projects/wiki/wd/mpk_lodz/quickstatements_routes.txt", "w", encoding="utf-8") as f:
    f.write(output)

log.info("Wygenerowano %d elementów tras (%d tram, %d autobus)", len(routes), stats['tram'], stats['bus'])
log.info("Linki do przystanków końcowych (P559): %d", stats['terminus_linked'])
log.info("Łączna liczba linków do przystanków: %d", stats['stops_linked'])
log.info("Podgląd (pierwsza trasa):\n%s", "\n".join(output.split("\n")[:20]))
