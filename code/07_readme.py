"""README.md and LICENSE, with numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
C = R["c"]; M = lambda v: f"{v / 1000:,.0f}"
readme = f"""# Every nuclear test

Every known nuclear test explosion from Trinity in 1945 to North Korea in 2017, mapped: where, by whom and how big. {R['n']:,} tests by eight countries, from the SIPRI list of nuclear explosions 1945 to 1998 (Bergkvist and Ferm 2000) and Wikipedia's list of North Korean tests, with the status of the land each test was on.

Interactive page: https://maps.tristanhotham.com/{SLUG}/
Paper: https://doi.org/{{10.5281/zenodo.23857489}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/nuclear-tests/}}

## Headline results

- {R['n']:,} tests, 1945 to 2017 (not counting Hiroshima and Nagasaki): {C['US']['n']:,} American, {C['USSR']['n']:,} Soviet, {C['France']['n']} French, {C['UK']['n']} British, {C['China']['n']} Chinese, {C['India']['n']} Indian, {C['Pakistan']['n']} Pakistani and {C['NKorea']['n']} North Korean.
- Testing peaked at {R['peak_n']} tests in {R['peak_year']}, one every {R['peak_days_per_test']:.1f} days; the tests of 1961 and 1962 released {R['yield_61_62_pct']:.0f}% of all test yield.
- After the 1963 Partial Test Ban Treaty testing went underground: {R['pre_atm_pct']:.0f}% of tests before it were atmospheric or underwater, {R['post_ug_pct']:.0f}% after it were underground. France tested in the atmosphere until 1974 and China until 1980.
- Total yield about {M(R['yield_total_mid'])} megatons (range {M(R['yield_total_lo'])} to {M(R['yield_total_hi'])}). The {R['mt_tests']} megaton-class tests carry {R['mt_tests_yield_pct']:.0f}% of it; Novaya Zemlya alone {R['nz_yield_pct']:.0f}%. Largest: Tsar Bomba, about 50 megatons, {R['tsar']['date']}; largest American: Castle Bravo, 15 megatons, 1954.
- Islands saw {R['island_pct']:.0f}% of tests but {R['island_yield_pct']:.0f}% of the yield. {R['away_n']} tests ({R['away_pct']:.0f}%, with {R['away_yield_pct']:.0f}% of the yield) were in colonies, overseas or trust territories or another state's territory, including every French and British test.
- {R['post_ctbt']['n']} tests since the Comprehensive Nuclear-Test-Ban Treaty opened for signature in 1996: India and Pakistan (2 each, 1998) and North Korea (6, 2006 to 2017).

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; results, notes, world outline and city names embedded; `data/points.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/tests.csv` | All {R['n_records']:,} records ({R['n']:,} tests and the two wartime bombs): date, country, site, position (and whether approximate), environment, method, purpose, yield low, high and midpoint (kt), seismic magnitudes, depth, name and source. |
| `data/tests_by_year_country.csv` | Tests per year and country, 1945 to 2017. |
| `data/sites.csv` | The {R['n_sites']} test sites: tests, years, atmospheric and underground counts, yield, status of the land, island flag. |
| `data/site_notes.json` | The short sourced notes on each site shown on the page and in the paper (CC BY-SA 4.0 where drawn from Wikipedia). |
| `data/countries.csv` | Totals by country. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/points.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data: test points (positions spread where tests share one), labels, Natural Earth outlines and city names. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates; `qa.js` takes screenshots with Playwright. |
| `release/` | Paper PDF and LaTeX source with figures, blog post with figures and meta, Zenodo files. |
| `reddit/` | Collage (`collage.py`, `every_nuclear_test.png`) and post text. |

## Method in brief

- Tests: the SIPRI list ({R['n_sipri']:,} explosions, 1945 to 1998) less Hiroshima and Nagasaki, plus North Korea's 6 tests from Wikipedia (dates, positions and yield ranges from the page table only). Salvoes count once, as in the SIPRI list, so totals are lower than Wikipedia's {R['wiki_tests']:,}.
- Yield: midpoint of the lower and upper estimates, with the sums of the lower and upper estimates given beside every total; {R['n_range_0']} tests are "0 to" some figure.
- Environment: atmospheric (air, tower, balloon, barge, ship, surface, rocket, space), underwater, underground (shaft, tunnel, gallery, mine, cratering).
- Sites: SIPRI site codes (with their spelling errors) mapped to {R['n_sites']} sites; {R['n_approx_pos']} records with no position placed approximately and flagged. Land status at the time of the test: own national territory; own colony, overseas or trust territory; another state's territory or colony; open ocean.
- Map: circle radius proportional to the cube root of yield; tests sharing an exact position spread over a small disc.
- Caveats: yields are estimates, often upper bounds; counts depend on how salvoes and safety trials are counted; post-1998 data from Wikipedia; this is a map of explosions, not of exposure or harm.

## How to rerun

Needs Python 3 with pandas, numpy, shapely, pyproj, matplotlib, fontTools, beautifulsoup4 and Pillow, xelatex and pdftotext; Node with Playwright for QA. Raw inputs are read in place from `/home/claude/newdata/raw8/nuclear/` and `/home/claude/newdata/raw/geo/` (set in `code/common.py`). Intermediate files go to `/dev/shm/nuclear/work` (set `NUCTMP` to change).

```
cd code
python3 01_clean.py        # tests, sites, environments, yields, North Korea, names
python3 02_geo.py          # world outline, country and city names
python3 03_results.py      # results.json and page data
python3 04_build_site.py   # index.html
python3 05_figures.py      # header, blog and paper figures
python3 06_paper.py        # paper PDF
python3 ../reddit/collage.py
python3 07_readme.py       # README and LICENSE
python3 08_release.py      # blog post, Zenodo files, Reddit post
```

## Sources and licences

- Bergkvist, N.-O. and Ferm, R. (2000) Nuclear Explosions 1945 to 1998. Stockholm: Swedish Defence Research Establishment (FOA) and Stockholm International Peace Research Institute (SIPRI). Data as published by data is plural (https://github.com/data-is-plural/nuclear-explosions) and rfordatascience/tidytuesday, 2019-08-20 (https://github.com/rfordatascience/tidytuesday/tree/main/data/2019/2019-08-20), credit Jesus Castagnetto.
- Wikipedia contributors (2026): List of nuclear weapons tests; List of nuclear weapons tests of North Korea; Pokhran-II; Chagai-I. CC BY-SA 4.0. Revisions in `code/common.py`. The North Korean records, test names from Wikipedia and the site notes drawing on Wikipedia are shared under CC BY-SA 4.0.
- UNSCEAR (2000) Annex C; Royal Commission into British Nuclear Tests in Australia (1985); Khalturin et al. (2005); Kuletz (1998): sources for site notes.
- Natural Earth countries and populated places (public domain). Base map tiles on the page: © Esri.

## Citation

Hotham, T. (2026) Every nuclear test: where, by whom and how big, from Trinity to North Korea, 1945 to 2017. Zenodo. https://doi.org/{{10.5281/zenodo.23857489}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in readme.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of the code in this repository (the code/
and reddit/ folders), to deal in the code without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the code, and to permit persons to whom the code is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the code.

THE CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE CODE OR THE USE OR OTHER DEALINGS IN THE CODE.

Text, figures and derived data

The text, figures, page and derived data are licensed under the Creative Commons Attribution 4.0 International licence
(CC BY 4.0, https://creativecommons.org/licenses/by/4.0/), with one exception: material derived from Wikipedia (the North
Korean test records, test names taken from Wikipedia, and the site notes that draw on Wikipedia) is shared under the
Creative Commons Attribution-ShareAlike 4.0 licence (CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/).
The test list is derived from Bergkvist and Ferm (2000), Nuclear Explosions 1945 to 1998 (FOA and SIPRI), as published
by data is plural and TidyTuesday. Please credit those sources as well as this work.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(readme.split()), "words")
