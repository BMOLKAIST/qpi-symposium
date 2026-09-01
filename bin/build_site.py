#!/usr/bin/env python3
"""Render index.html and past/index.html from _data/editions.json.

The site is plain static HTML — there is no CI build. Run this locally after
editing the data, check the output in a browser, then commit both the JSON and
the generated HTML.

Usage:
    python3 bin/build_editions.py   # register -> _data/editions.json
    python3 bin/build_site.py       # editions.json -> html
"""

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "editions.json"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500'
    "&family=Inter:wght@400;500;600&display=swap\" rel=\"stylesheet\">"
)


def e(s):
    return html.escape(str(s), quote=True)


# Hyphenated technical compounds that should never be split across lines. A
# browser treats the hyphen as a break opportunity, so "three-dimensional" can
# end a line as "three-" with "dimensional" orphaned below, which reads as a
# forced break. Emitting a non-breaking hyphen says these are single words.
#
# This is not the same as hard-coding a break point with &nbsp; — we are not
# choosing where lines break, only stating which strings are indivisible.
TIGHT_COMPOUNDS = (
    "three-dimensional",
    "label-free",
    "on-site",
    "in-person",
    "co-chair",
    "real-time",
    "high-throughput",
)


def protect_compounds(markup):
    """Replace the hyphen in known compounds with &#8209; (non-breaking)."""
    for word in TIGHT_COMPOUNDS:
        markup = markup.replace(word, word.replace("-", "&#8209;"))
        cap = word[0].upper() + word[1:]
        markup = markup.replace(cap, cap.replace("-", "&#8209;"))
    return markup


def head(title, description, css_path, canonical):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:type" content="website">
  <link rel="canonical" href="{e(canonical)}">
  {FONTS}
  <link rel="stylesheet" href="{css_path}">
</head>
<body>"""


def topbar(root, here):
    def cls(page):
        return ' aria-current="page"' if page == here else ""

    return f"""
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="{root}">QPI Symposium</a>
    <nav class="navlinks">
      <a href="{root}"{cls('home')}>2026</a>
      <a href="{root}past/"{cls('past')}>Past editions</a>
    </nav>
  </div>
</header>"""


def footer(root, series):
    return f"""
<footer>
  <div class="wrap">
    <p>{e(series['name'])} — held since {series['since']}.</p>
    <p>Organized by KAIST, Seoul National University and The Chinese University of Hong Kong.</p>
    <p>Earlier editions were announced on the <a href="https://bmokaist.wordpress.com/webinar/">previous events page</a>. This site is now the current record.</p>
  </div>
</footer>
</body>
</html>
"""


def build_index(data):
    cur = data["current"]
    series = data["series"]
    title = f"{cur['title']} — {cur['location']}, {cur['date_display']}"
    desc = (
        f"The {cur['label']} Quantitative Phase Imaging Symposium, "
        f"{cur['date_display']}, at {cur['venue']}, {cur['location']}."
    )

    schedule = "\n".join(
        f"""      <li><div class="day">{e(s['day'])}</div><div class="what">{e(s['what'])}</div></li>"""
        for s in cur["schedule"]
    )

    def person_card(o):
        photo = o.get("photo")
        if photo:
            face = f'<img class="face" src="assets/img/people/{e(photo)}" alt="{e(o["name"])}" loading="lazy" width="640" height="640">'
        else:
            # No portrait yet. Show initials rather than a broken image.
            initials = "".join(w[0] for w in o["name"].replace("(", "").replace(")", "").split()[:2]).upper()
            face = f'<div class="face placeholder" aria-hidden="true">{e(initials)}</div>'
        return (
            f'      <div class="person">{face}'
            f'<div class="n">{e(o["name"])}</div>'
            f'<div class="a">{e(o["affiliation"])}</div>'
            f'<div class="r">{e(o["role"])}</div></div>'
        )

    people = "\n".join(person_card(o) for o in data["organizers"])

    past_count = len(data["past"])
    talk_count = sum(p["speaker_count"] for p in data["past"])

    reg = cur.get("registration") or {}
    if reg.get("url"):
        reg_fact = e(reg.get("fee", "Free"))
        reg_btn = f'<a class="btn" href="{e(reg["url"])}">Register</a>\n      '
        reg_section = (
            f'<p><a class="btn" href="{e(reg["url"])}">Register</a></p>'
            f'<p style="margin-top:1rem">Attendance is {e(reg.get("fee", "free")).lower()}. '
            "Poster submissions are made through the same form.</p>"
        )
    else:
        reg_fact = f'{e(reg.get("fee", "Free"))} &middot; opens soon'
        reg_btn = ""
        reg_section = f'<p class="notice">{e(reg.get("note", "Registration will open here."))}</p>'


    return f"""{head(title, desc, "assets/css/style.css", "https://bmolkaist.github.io/qpi-symposium/")}
{topbar("", "home")}

<div class="hero">
  <div class="wrap">
    <p class="eyebrow">{e(cur['label'])} Symposium &middot; {e(cur['location'])}</p>
    <h1>Quantitative Phase Imaging Symposium 2026</h1>
    <p class="lede">{e(series['about'])}</p>
    <div class="facts">
      <div><div class="k">Dates</div><div class="v">{e(cur['date_display'])}</div></div>
      <div><div class="k">Venue</div><div class="v">{e(cur['venue'])}</div></div>
      <div><div class="k">Format</div><div class="v">{e(cur['format'])}</div></div>
      <div><div class="k">Registration</div><div class="v">{reg_fact}</div></div>
    </div>
    <div class="btnrow">
      {reg_btn}<a class="btn ghost" href="past/">Past editions</a>
    </div>
  </div>
</div>

<figure class="band">
  <img src="assets/img/lake.jpg" alt="Lake Ad Excellentiam on the CUHK campus" width="2000" height="700">
</figure>

<section>
  <div class="wrap">
    <h2>Programme</h2>
    <p>The scientific programme runs for a full day on the Friday, with a welcome reception the evening before and an excursion on the Saturday.</p>
    <ul class="schedule">
{schedule}
    </ul>
    <p style="margin-top:1.75rem">The day is built around <strong>six invited talks</strong>, three in the morning and three in the afternoon, together with a poster session. Selected posters are introduced in a short lightning round, and participants vote for the best poster.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Scope</h2>
    <p>The symposium is <strong>not limited to biological applications</strong>. Industrial work — semiconductor and precision metrology, inspection — and adjacent fields such as atomic electron tomography are equally welcome. The common ground is quantitative phase and imaging, not the sample.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Invited speakers</h2>
    <p class="notice">The 2026 speaker list is being finalised and will be announced here. Across the {past_count} previous editions the symposium has hosted <strong>{talk_count} invited talks</strong> — see <a href="past/">past editions</a>.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Registration</h2>
    {reg_section}
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Venue and travel</h2>
    <p>The meeting is held at <strong>{e(cur['venue'])}</strong>. Most international visitors do not require a visa to enter Hong Kong, which makes this an unusually easy meeting to reach for colleagues across the region. Information on accommodation will be posted here.</p>
    <figure class="shot">
      <img src="assets/img/campus.jpg" alt="The CUHK campus on its hillside above Sha Tin" width="2000" height="800" loading="lazy">
      <figcaption>The CUHK campus. Photo: Citobun, <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a></figcaption>
    </figure>
    <p style="margin-top:1.75rem">Saturday is given over to an excursion, so there is time to see the city as well as the meeting.</p>
    <figure class="shot">
      <img src="assets/img/harbour.jpg" alt="Victoria Harbour at night" width="2000" height="800" loading="lazy">
      <figcaption>Victoria Harbour. Photo: Benh Lieu Song, <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></figcaption>
    </figure>
    <p style="margin-top:1.75rem">The symposium is <strong>in person only</strong> — there is no online attendance. Bringing the community into one room for a day is the point of the meeting, and remote participation has not served that well in the past.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Organizers</h2>
    <div class="people">
{people}
    </div>
  </div>
</section>
{footer("", series)}"""


def build_past(data):
    series = data["series"]
    title = "Past editions — QPI Symposium"
    desc = (
        "Programmes and invited speakers from every previous Quantitative Phase "
        "Imaging Symposium, from the first online workshop in 2020."
    )

    blocks = []
    for ed in data["past"]:
        rows = "\n".join(
            f"""          <tr><td>{e(s['name'])}"""
            f"""{'<span class="kn">Keynote</span>' if s.get('keynote') else ''}</td>"""
            f"""<td>{e(s['affiliation'])}</td><td>{e(s['region'])}</td></tr>"""
            for s in ed["speakers"]
        )
        note = f'      <p class="edition-note">{e(ed["note"])}</p>\n' if ed["note"] else ""
        blocks.append(
            f"""  <article class="edition">
      <div class="edition-head">
        <h2>{e(ed['label'])} Symposium</h2>
        <span class="badge">{e(ed['format'])}</span>
      </div>
      <p class="edition-meta">{e(ed['date_display'])} &middot; {e(ed['venue'])}, {e(ed['location'])} &middot; {ed['speaker_count']} invited talks</p>
{note}      <div class="tablewrap">
        <table class="speakers">
          <thead><tr><th>Speaker</th><th>Affiliation</th><th>Region</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
  </article>"""
        )

    total = sum(p["speaker_count"] for p in data["past"])

    return f"""{head(title, desc, "../assets/css/style.css", "https://bmolkaist.github.io/qpi-symposium/past/")}
{topbar("../", "past")}

<div class="hero">
  <div class="wrap">
    <p class="eyebrow">Archive</p>
    <h1>Past editions</h1>
    <p class="lede">Five editions since 2020 and {total} invited talks. Affiliations are given as they stood at the time of each talk.</p>
  </div>
</div>

<section>
  <div class="wrap">
{chr(10).join(blocks)}
  </div>
</section>
{footer("../", series)}"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    (ROOT / "index.html").write_text(protect_compounds(build_index(data)), encoding="utf-8")
    (ROOT / "past").mkdir(exist_ok=True)
    (ROOT / "past" / "index.html").write_text(
        protect_compounds(build_past(data)), encoding="utf-8"
    )
    print("wrote index.html")
    print("wrote past/index.html")


if __name__ == "__main__":
    main()
