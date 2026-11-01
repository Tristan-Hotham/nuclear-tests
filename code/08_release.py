"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo), Reddit post text (reddit/post.md).
10.5281/zenodo.23857489, https://doi.org/10.5281/zenodo.23857489 and https://blog.tristanhotham.com/2026/10/31/nuclear-tests/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Every_Nuclear_Test"
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "04_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))

# numbers written in words or alt text in the blog and post
Y = {r[0]: sum(r[1:]) for r in R["years"]}
assert Y[1958] == 116 and Y[1962] == 178 and Y[1959] == 0 and Y[1960] == 3
assert all(30 <= Y[y] <= 80 for y in range(1963, 1985)) and max(Y[y] for y in range(1999, 2018)) <= 2
assert [round(k["pct"]) for k in R["kinds"][:2]] == [82, 14] and [round(k["yield_pct"]) for k in R["kinds"][:2]] == [68, 27]
assert round(R["island_pct"]) == 21 and round(R["island_yield_pct"]) == 84
S = R["site"]
assert [round(S[k]["yield_mid"] / 1000) for k in ("novaya", "bikini", "nevada", "enewetak", "kiritimati", "lopnur", "johnston", "semipalatinsk", "moruroa")] == [281, 77, 46, 32, 30, 21, 21, 18, 10]
assert R["top20_ussr"] == 11 and R["top20_us"] == 9 and R["top20_1961_62"] == 12
assert 20000 <= R["biggest"][1]["mid"] <= 30000 and R["biggest"][6]["name"] == "Castle Yankee" and R["biggest"][6]["mid"] == 13500
assert R["median_kt"] < R["hiroshima_kt"]
assert R["peak_days_per_test"] < 2.1                                       # "one every two days"
assert R["c"]["USSR"]["last_year"] == 1990 and R["c"]["UK"]["last_year"] == 1991 and R["c"]["US"]["last_year"] == 1992
assert R["post_ctbt"]["by"] == {"India": 2, "Pakistan": 2, "NKorea": 6}
assert round(R["pre_atm_pct"]) == 79 and round(R["post_ug_pct"]) == 95
assert R["c"]["France"]["last_atm_year"] == 1974 and R["c"]["China"]["last_atm_year"] == 1980

post = fill(open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read(), R)
post = post.replace("Novaya Zemlya leads with about 280 megatons", f"Novaya Zemlya leads with about {round(S['novaya']['yield_mid'] / 1000)} megatons")
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u), post, re.M) for u in used) and "wp:image" not in post
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Every nuclear test, mapped",
        "slug": "nuclear-tests",
        "excerpt": f"Since 1945 eight countries have set off {R['n']:,} nuclear tests. I mapped every one: {R['peak_n']} in {R['peak_year']} alone, most of them underground after 1963, and {R['island_yield_pct']:.0f}% of all the explosive yield on islands.",
        "seo_description": f"Every nuclear test since 1945 mapped: {R['n']:,} tests by eight countries, the 1962 peak, the move underground, and whose land they were on.",
        "tags": ["nuclear weapons", "nuclear testing", "maps", "data visualisation", "Cold War", "Marshall Islands", "French Polynesia", "Semipalatinsk", "open data"],
        "header_alt": f"Title card reading 'Every nuclear test' in black and red on pale paper, beside a world map with circles at every nuclear test site, sized by yield and coloured by country: large red circles on Novaya Zemlya, blue on the Pacific atolls and Nevada, gold at Lop Nur. Text: {R['n']:,} tests by eight countries, 1945 to 2017; {R['peak_n']} in {R['peak_year']} alone; {R['island_yield_pct']:.0f}% of all the explosive yield was set off on islands."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/nuclear-tests_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"nuclear-tests/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"nuclear-tests/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "nuclear-tests/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("~", " ")
zmeta = {"title": "Every Nuclear Test: Where, by Whom and How Big, from Trinity to North Korea, 1945 to 2017",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/nuclear-tests/}}.</p><p>Data: Bergkvist and Ferm (2000), Nuclear Explosions 1945 to 1998 (FOA and SIPRI), via data is plural and TidyTuesday; Wikipedia (CC BY-SA 4.0); Natural Earth. Text, figures and derived data CC BY 4.0, except material derived from Wikipedia, which is CC BY-SA 4.0; code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["nuclear weapons testing", "nuclear tests", "Partial Test Ban Treaty", "Comprehensive Nuclear-Test-Ban Treaty", "Marshall Islands", "French Polynesia", "Semipalatinsk", "Novaya Zemlya", "SIPRI", "open data", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://github.com/data-is-plural/nuclear-explosions", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://github.com/rfordatascience/tidytuesday/tree/main/data/2019/2019-08-20", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://en.wikipedia.org/wiki/List_of_nuclear_weapons_tests_of_North_Korea", "relation": "isDerivedFrom", "resource_type": "other"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")

# Reddit post text
post_md = f"""## Title

[OC] Every nuclear test since 1945, mapped: {R['n']:,} explosions by eight countries, {R['peak_n']} in {R['peak_year']} alone, and {R['island_yield_pct']:.0f}% of all the explosive yield was set off on islands

## Body

I mapped every nuclear test in the SIPRI list of nuclear explosions (Bergkvist and Ferm 2000, 1945 to 1998) plus North Korea's six tests from 2006 to 2017: {R['n']:,} tests, not counting Hiroshima and Nagasaki. Circles are sized by the cube root of yield, the way blast damage scales. Testing peaked at {R['peak_n']} tests in {R['peak_year']}, one every two days, after a pause from 1958 to 1961. After the 1963 Partial Test Ban Treaty {R['post_ug_pct']:.0f}% of tests were underground, but France and China kept testing in the atmosphere until 1974 and 1980. The total yield was about {R['yield_total_mid'] / 1000:,.0f} megatons (range {R['yield_total_lo'] / 1000:,.0f} to {R['yield_total_hi'] / 1000:,.0f}); Novaya Zemlya alone took {R['nz_yield_pct']:.0f}%, and islands {R['island_yield_pct']:.0f}%, though they saw only {R['island_pct']:.0f}% of tests. Every French and British test was outside the home country, in Algeria, French Polynesia, Australia, the central Pacific and Nevada. Caveats: yields are estimates, often only "less than" some figure, so I use the middle of each range; counts differ between sources depending on how salvoes are counted. Interactive map with a year slider and a filter for atmospheric and underground tests: https://maps.tristanhotham.com/nuclear-tests/

## Source comment

Sources: Bergkvist, N.-O. and Ferm, R. (2000) Nuclear Explosions 1945 to 1998, FOA and SIPRI, via data is plural (https://github.com/data-is-plural/nuclear-explosions) and TidyTuesday 2019-08-20 (credit Jesus Castagnetto); Wikipedia, List of nuclear weapons tests of North Korea and List of nuclear weapons tests (CC BY-SA 4.0); Natural Earth outlines (public domain).

Tools: Python (pandas, shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/nuclear-tests/
Paper: https://doi.org/{{10.5281/zenodo.23857489}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/nuclear-tests/}}
"""
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in post_md, bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post_md)
print("reddit title chars", len(post_md.splitlines()[2]))
