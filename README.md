# QPI Symposium

Site for the Quantitative Phase Imaging Symposium — https://bmolkaist.github.io/qpi-symposium/

Plain static HTML. There is no CI build: the pages are generated locally and committed.

## Editing

All edition data lives in one place, `_data/editions.json`. Past-edition speakers are
generated from the vault register (`Conferences/_data/qpi-invited-speakers.csv`).

    python3 bin/build_editions.py   # register -> _data/editions.json
    python3 bin/build_site.py       # editions.json -> index.html, past/index.html
    python3 -m http.server 8899     # preview at http://localhost:8899

Commit both the JSON and the generated HTML.

## Adding a new edition

1. Move the current edition's block from `CURRENT` into `EDITIONS` in `bin/build_editions.py`
2. Write the new `CURRENT`
3. Refresh `bin/speakers-source.csv` from the vault register
4. Re-run both scripts, preview, commit

## Opening registration

Create a **new** Google Form for each edition, owned by whoever handles registration
that year, then set the URL in `bin/build_editions.py`:

    "registration": {"url": "https://forms.gle/...", "fee": "Free", "note": ""}

Re-run both scripts. The Register button appears automatically; while `url` is
`None` the page says registration opens soon instead.

Never point at a previous edition's form — responses land in that year's sheet and
the form text names the wrong dates and venue.

## Images

Web copies live in `assets/img/`. Originals and the untouched downloads are kept
outside the repo; the versions here are cropped to the band ratio and toned down
(saturation and brightness reduced, contrast curve applied) so they sit on the
black canvas instead of punching a bright hole in it.

Credits are required for the CC BY-SA photographs and are written into the
figure captions. Do not remove them.

Organizer portraits go in `assets/img/people/`. Ask each person for a photo —
never take one from a department page. Until someone sends one their card shows
their initials, which is why there is no broken-image placeholder in the repo.

## Conventions

- English only.
- Do not publish invited speakers before they have accepted.
- Never hard-code line breaks with `&nbsp;` or `<br>`. Headings use
  `text-wrap: balance` and paragraphs `text-wrap: pretty` — the right break
  depends on the viewport, which we cannot know when writing the markup.
- Hyphenated technical compounds are the one exception, and only because a
  hyphen is a break opportunity: "three-dimensional" can end a line as "three-".
  `protect_compounds()` in `bin/build_site.py` emits a non-breaking hyphen for
  the terms listed there. That states which strings are indivisible; it does not
  choose where lines break. Add new compounds to that list rather than editing
  the text.
