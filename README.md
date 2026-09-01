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

## Conventions

- English only.
- Do not publish invited speakers before they have accepted.
