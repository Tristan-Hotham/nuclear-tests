# Every nuclear test

Every known nuclear test explosion from Trinity in 1945 to North Korea in 2017, mapped: where, by whom and how big. 2,055 tests by eight countries, from the SIPRI list of nuclear explosions 1945 to 1998 (Bergkvist and Ferm 2000) and Wikipedia's list of North Korean tests, with the status of the land each test was on.

Interactive page: https://maps.tristanhotham.com/nuclear-tests/
Paper: https://doi.org/10.5281/zenodo.23857489
Blog post: https://blog.tristanhotham.com/2026/10/31/nuclear-tests/

## Headline results

- 2,055 tests, 1945 to 2017 (not counting Hiroshima and Nagasaki): 1,030 American, 714 Soviet, 210 French, 45 British, 45 Chinese, 3 Indian, 2 Pakistani and 6 North Korean.
- Testing peaked at 178 tests in 1962, one every 2.1 days; the tests of 1961 and 1962 released 50% of all test yield.
- After the 1963 Partial Test Ban Treaty testing went underground: 79% of tests before it were atmospheric or underwater, 95% after it were underground. France tested in the atmosphere until 1974 and China until 1980.
- Total yield about 546 megatons (range 429 to 664). The 85 megaton-class tests carry 80% of it; Novaya Zemlya alone 51%. Largest: Tsar Bomba, about 50 megatons, 30 October 1961; largest American: Castle Bravo, 15 megatons, 1954.
- Islands saw 21% of tests but 84% of the yield. 357 tests (17%, with 32% of the yield) were in colonies, overseas or trust territories or another state's territory, including every French and British test.
- 10 tests since the Comprehensive Nuclear-Test-Ban Treaty opened for signature in 1996: India and Pakistan (2 each, 1998) and North Korea (6, 2006 to 2017).

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/04_build_site.py`; results, notes, world outline and city names embedded; `data/points.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/tests.csv` | All 2,057 records (2,055 tests and the two wartime bombs): date, country, site, position (and whether approximate), environment, method, purpose, yield low, high and midpoint (kt), seismic magnitudes, depth, name and source. |
| `data/tests_by_year_country.csv` | Tests per year and country, 1945 to 2017. |
| `data/sites.csv` | The 27 test sites: tests, years, atmospheric and underground counts, yield, status of the land, island flag. |
| `data/site_notes.json` | The short sourced notes on each site shown on the page and in the paper (CC BY-SA 4.0 where drawn from Wikipedia). |
| `data/countries.csv` | Totals by country. |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/points.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data: test points (positions spread where tests share one), labels, Natural Earth outlines and city names. |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates; `qa.js` takes screenshots with Playwright. |
| `release/` | Paper PDF and LaTeX source with figures, blog post with figures and meta, Zenodo files. |
| `reddit/` | Collage (`collage.py`, `every_nuclear_test.png`) and post text. |

## Method in brief

- Tests: the SIPRI list (2,051 explosions, 1945 to 1998) less Hiroshima and Nagasaki, plus North Korea's 6 tests from Wikipedia (dates, positions and yield ranges from the page table only). Salvoes count once, as in the SIPRI list, so totals are lower than Wikipedia's 2,121.
- Yield: midpoint of the lower and upper estimates, with the sums of the lower and upper estimates given beside every total; 776 tests are "0 to" some figure.
- Environment: atmospheric (air, tower, balloon, barge, ship, surface, rocket, space), underwater, underground (shaft, tunnel, gallery, mine, cratering).
- Sites: SIPRI site codes (with their spelling errors) mapped to 27 sites; 24 records with no position placed approximately and flagged. Land status at the time of the test: own national territory; own colony, overseas or trust territory; another state's territory or colony; open ocean.
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

Hotham, T. (2026) Every nuclear test: where, by whom and how big, from Trinity to North Korea, 1945 to 2017. Zenodo. https://doi.org/10.5281/zenodo.23857489

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
