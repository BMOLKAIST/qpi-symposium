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

    def person_card(o, speaker=False):
        photo = o.get("photo")
        if photo:
            face = f'<img class="face" src="assets/img/people/{e(photo)}" alt="{e(o["name"])}" loading="lazy" width="640" height="640">'
        else:
            # No portrait yet. Show initials rather than a broken image.
            initials = "".join(w[0] for w in o["name"].replace("(", "").replace(")", "").split()[:2]).upper()
            face = f'<div class="face placeholder" aria-hidden="true">{e(initials)}</div>'
        if speaker:
            title = o.get("title")
            talk = f'<p class="speaker-title">{e(title)}</p>' if title else ""
            return (
                f'<li class="speaker-row">{face}<div class="speaker-details">'
                f'<h3>{e(o["name"])}</h3>'
                f'<p class="speaker-affiliation">{e(o["affiliation"])}</p>'
                f'{talk}</div></li>'
            )
        return (
            f'      <div class="person">{face}'
            f'<div class="n">{e(o["name"])}</div>'
            f'<div class="a">{e(o["affiliation"])}</div>'
            f'<div class="r">{e(o["role"])}</div></div>'
        )

    people = "\n".join(person_card(o) for o in data["organizers"])

    speakers = "\n".join(person_card(o, speaker=True) for o in cur.get("speakers", []))
    committee = "\n".join(person_card(o) for o in cur.get("program_committee", []))
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
            f'<p><strong>Poster abstract deadline: {e(cur["poster_deadline"])}.</strong></p>'
            '<p>Complimentary conference dinner places are offered to advance registrants '
            'on a first-come, first-served basis, subject to availability. The current '
            'reservation is for 50 people; dinner capacity is separate from registration capacity.</p>'

        )
    else:
        reg_fact = f'{e(reg.get("fee", "Free"))} &middot; opens soon'
        reg_btn = ""
        reg_section = f'<p class="notice">{e(reg.get("note", "Registration will open here."))}</p>'


    return f"""{head(title, desc, "assets/css/style.css?v=20260924-speakers", "https://bmolkaist.github.io/qpi-symposium/")}
{topbar("", "home")}

<div class="hero">
  <div class="wrap">
    <p class="eyebrow">{e(cur['label'])} Symposium &middot; {e(cur['location'])}</p>
    <h1>Quantitative Phase Imaging<br>Symposium 2026</h1>
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
    <h2>Preliminary programme</h2>
    <p>Updated {e(cur["updated"])}. All times are Hong Kong time (HKT, UTC+8). Detailed talk times, titles and speaker order will follow.</p>
    <p>The scientific programme runs for a full day on the Friday, with a welcome dinner the evening before and optional informal scientific discussions planned for Saturday.</p>
    <ul class="schedule">
{schedule}
    </ul>
    <p style="margin-top:1.75rem">The day is planned around <strong>six invited talks of 40 minutes each, including discussion</strong>, three in the morning and three in the afternoon, together with a poster session. Approximately four selected posters will be introduced in five-minute lightning talks, and participants will vote for the best poster. Coffee breaks are planned for 20 minutes. Lunch for chairs and invited speakers is booked for 12:00 at CC Staff Canteen.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Scope</h2>
    <p>Quantitative phase imaging measures the optical path a specimen imposes on light, and that single measurement carries a long way. It gives dry mass and refractive index in a living cell, surface figure and film thickness on a semiconductor wafer or a glass substrate, and — through the same phase retrieval — structure at atomic resolution in electron tomography.</p>
    <p style="margin-top:1.25rem">The symposium is built around <strong>the measurement rather than the specimen</strong>. Talks run from optics and reconstruction algorithms through biology and medicine to materials, metrology and inspection, and we would rather the programme were broad than tidy.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Invited speakers</h2>
    <p>Confirmed speakers, listed alphabetically by surname. All invited talks take place on Friday, 20 November. One further invited speaker will be announced once confirmed.</p>
    <ul class="speaker-list">
{speakers}
    </ul>
    <p>Talk titles and abstracts will be added as they become available.</p>
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
    <p>The meeting is held at <strong>{e(cur['venue'])}</strong>. The scientific sessions and posters will be in <strong>{e(cur["venue_room"])}</strong>. For travel or visa-support coordination, contact <a href="mailto:qhzhang@cuhk.edu.hk">Qihang Zhang</a>.</p>
    <p>The local team is coordinating hotel arrangements and a possible group discount at Hyatt Regency Hong Kong, Sha Tin. Booking instructions will follow.</p>
    <figure class="shot">
      <img src="assets/img/campus.jpg" alt="The CUHK campus on its hillside above Sha Tin" width="2000" height="800" loading="lazy">
      <figcaption>The CUHK campus. Photo: Citobun, <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a></figcaption>
    </figure>
    <p style="margin-top:1.75rem">Further details of the optional Saturday discussions will be announced at the symposium.</p>
    <figure class="shot">
      <img src="assets/img/harbour.jpg" alt="Victoria Harbour at night" width="2000" height="800" loading="lazy">
      <figcaption>Victoria Harbour. Photo: Benh Lieu Song, <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></figcaption>
    </figure>
    <p style="margin-top:1.75rem">The symposium is <strong>in person only</strong> — there is no online attendance. Bringing the community into one room for a day is the point of the meeting, and remote participation has not served that well in the past.</p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Symposium chairs</h2>
    <div class="people">
{people}
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <h2>Program committee</h2>
    <div class="people">
{committee}
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
