#!/usr/bin/env python3
"""Generate _data/editions.json from the vault speaker register.

The register (Conferences/_data/qpi-invited-speakers.csv in the Obsidian vault)
is the single source of truth for who spoke at which edition. Edition metadata
— dates, venue, format — lives here, since it is not in the register.

Usage:
    python3 bin/build_editions.py [path/to/qpi-invited-speakers.csv]

Re-run after updating the register; commit the regenerated JSON.
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "bin" / "speakers-source.csv"
OUT = ROOT / "_data" / "editions.json"

# Edition metadata. Ordinal is the number used publicly; note that 2022 was
# skipped, so ordinals do not track calendar years.
EDITIONS = [
    {
        "ordinal": 1,
        "label": "1st",
        "title": "KAIST e-workshop on Quantitative Phase Imaging 2020",
        "date_display": "23 December 2020",
        "date_sort": "2020-12-23",
        "venue": "Online",
        "location": "Zoom",
        "format": "Online only",
        "note": "The first meeting, held online during the pandemic and hosted by KAIST alone.",
    },
    {
        "ordinal": 2,
        "label": "2nd",
        "title": "Quantitative Phase Imaging 2021 — From label-free imaging to biomedical applications",
        "date_display": "22 December 2021",
        "date_sort": "2021-12-22",
        "venue": "Online",
        "location": "Zoom",
        "format": "Online only",
        "note": "The edition at which the meeting was established as a recurring series and the joint organizing committee was formed.",
    },
    {
        "ordinal": 3,
        "label": "3rd",
        "title": "The 3rd Quantitative Phase Imaging Symposium",
        "date_display": "15 March 2023",
        "date_sort": "2023-03-15",
        "venue": "KAIST",
        "location": "Daejeon, Korea",
        "format": "Hybrid",
        "note": "The first in-person edition. A poster session with selected short talks became a standing part of the programme.",
    },
    {
        "ordinal": 4,
        "label": "4th",
        "title": "The 4th Quantitative Phase Imaging Symposium",
        "date_display": "23 August 2024",
        "date_sort": "2024-08-23",
        "venue": "KAIST",
        "location": "Daejeon, Korea",
        "format": "Hybrid",
        "note": "",
    },
    {
        "ordinal": 5,
        "label": "5th",
        "title": "The 5th Quantitative Phase Imaging Symposium",
        "date_display": "5 June 2025",
        "date_sort": "2025-06-05",
        "venue": "KAIST",
        "location": "Daejeon, Korea",
        "format": "Hybrid",
        "note": "",
    },
]

CURRENT = {
    "ordinal": 6,
    "label": "6th",
    "title": "The 6th Quantitative Phase Imaging Symposium",
    # Public-facing dates cover the meeting proper. The Thursday reception is
    # for chairs and invited speakers only, so advertising 19-21 would imply
    # that general attendees need to arrive a day earlier than they do. The
    # KAIST grant period is still 19-21 and covers the reception.
    "date_display": "20–21 November 2026",
    "date_sort": "2026-11-20",
    "venue": "The Chinese University of Hong Kong",
    "location": "Hong Kong",
    "format": "In person",
    "schedule": [
        {"day": "Thursday 19 November", "what": "Welcome reception (chairs and invited speakers)"},
        {"day": "Friday 20 November", "what": "Scientific programme, followed by dinner"},
        {"day": "Saturday 21 November", "what": "Excursion"},
    ],
    "speakers_status": "to-be-announced",
    # Registration. Set "url" once the form exists; the button appears only then.
    # Do not reuse a previous edition's form — responses would land in its sheet.
    "registration": {
        "url": None,
        "fee": "Free",
        "note": "Registration opens in September.",
    },
}

# "photo" is a filename under assets/img/people/, or None until the person has
# sent one. Never take a portrait from a department page — it is someone else's
# copyright and their likeness, and they should pick which photo of them goes up.
ORGANIZERS = [
    {"name": "YongKeun (Paul) Park", "affiliation": "KAIST", "role": "Chair",
     "photo": "yongkeun-park.jpg"},
    {"name": "Seung Ah Lee", "affiliation": "Seoul National University", "role": "Co-chair",
     "photo": None},
    {"name": "Renjie Zhou", "affiliation": "The Chinese University of Hong Kong", "role": "Co-chair, local host",
     "photo": None},
    {"name": "Yongsoo Yang", "affiliation": "KAIST", "role": "Co-chair",
     "photo": None},
]

# Roles that should not be shown as an invited talk on the public archive.
SKIP_ROLES = {"organizer"}


def load_speakers(csv_path):
    """Return {edition_ordinal: [speaker, ...]} for the Symposium series."""
    by_edition = {}
    with open(csv_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["venue"] != "Symposium":
                continue
            if row["status"] != "presented":
                continue
            ordinal = int(row["edition"])
            entry = {
                "name": row["speaker"],
                "affiliation": row["affiliation"],
                "region": row["region"],
            }
            if row["role"] == "keynote":
                entry["keynote"] = True
            by_edition.setdefault(ordinal, []).append(entry)
    return by_edition


def main():
    csv_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not csv_path.exists():
        sys.exit(f"register not found: {csv_path}")

    by_edition = load_speakers(csv_path)

    past = []
    for meta in EDITIONS:
        speakers = by_edition.get(meta["ordinal"], [])
        entry = dict(meta)
        entry["speakers"] = speakers
        entry["speaker_count"] = len(speakers)
        past.append(entry)

    past.sort(key=lambda e: e["date_sort"], reverse=True)

    data = {
        "series": {
            "name": "Quantitative Phase Imaging Symposium",
            "short": "QPI Symposium",
            "since": 2020,
            "about": (
                "An annual gathering of the quantitative phase imaging community in Asia, "
                "bringing groups in the region together in person to share recent work in "
                "label-free, quantitative and three-dimensional imaging."
            ),
        },
        "current": CURRENT,
        "organizers": ORGANIZERS,
        "past": past,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total = sum(e["speaker_count"] for e in past)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  past editions : {len(past)}")
    print(f"  invited talks : {total}")
    for e in past:
        print(f"    {e['label']:4} {e['date_sort']}  {e['speaker_count']:2} speakers  {e['venue']}")


if __name__ == "__main__":
    main()
