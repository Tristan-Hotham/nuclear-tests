"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (results, site.json, site notes, world outline, cities) is embedded; data/points.json is
loaded by the page. Facts stated in words on the page are checked here. 10.5281/zenodo.23857489 and https://blog.tristanhotham.com/2026/10/31/nuclear-tests/ stay as placeholders.

NOTES are the short site notes shown on the page, in the paper's site table and the side panel. Each states plain facts
with its source in brackets: the Wikipedia pages listed in common.py (CC BY-SA), UNSCEAR (2000), the Royal Commission into
British Nuclear Tests in Australia (1985), Khalturin et al. (2005), Kuletz (1998), and the counts in data/results.json."""
import json
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
SITEJ = jload(f"{DATA}/site.json")
WIKI = jload(f"{WORK}/wiki.json")

NOTES = {
    "nevada": "The main US test site from {{site.nevada.y0|raw}} to {{site.nevada.y1|raw}}, in the desert north of Las Vegas, on land the Western Shoshone claim under the 1863 Treaty of Ruby Valley (Kuletz 1998). {{uk_at_nevada|int}} British tests were also held here. Fallout from the atmospheric tests of the 1950s drifted over communities downwind (UNSCEAR 2000).",
    "trinity": "The first nuclear test, on 16 July 1945, on the Alamogordo bombing range in the New Mexico desert.",
    "usmain": "Peaceful and research explosions: gas well stimulation in New Mexico and Colorado, and shots in salt in New Mexico and Mississippi (SIPRI purposes).",
    "amchitka": "Three underground tests in the Aleutian Islands of Alaska, including Cannikin in 1971, the largest US underground test (Wikipedia).",
    "bikini": "In the Marshall Islands, from 1947 a UN trust territory administered by the United States. Its people were moved off before the first tests in 1946 (UNSCEAR 2000). Fallout from Castle Bravo in 1954 reached the inhabited Rongelap and Rongerik atolls, which were evacuated (Wikipedia).",
    "enewetak": "Marshall Islands, a UN trust territory administered by the United States. Its people were moved to Ujelang Atoll in 1947 (UNSCEAR 2000). Ivy Mike, the first full scale hydrogen bomb, was fired here in 1952.",
    "johnston": "A small US-held atoll in the central Pacific with no permanent population, used for high altitude rocket shots in 1958 and 1962.",
    "kiritimati": "Then part of a British colony in the central Pacific, now Kiribati. Britain tested hydrogen bombs here in 1957 and 1958, and the United States fired {{kiribati.us|int}} air drops nearby in 1962 (Wikipedia).",
    "malden": "An uninhabited British-held island in the central Pacific, now part of Kiribati: Britain's first hydrogen bomb trials, 1957 (Wikipedia).",
    "ocean": "Shots fired far from land, over or under the open Pacific and, in 1958, high above the South Atlantic.",
    "semipalatinsk": "The main Soviet test site, on the steppe of the Kazakh Soviet republic, used from {{site.semipalatinsk.y0|raw}} to {{site.semipalatinsk.y1|raw}}. People living in villages nearby were exposed to fallout from the early tests (UNSCEAR 2000). Kazakhstan closed the site on 29 August 1991, the date the United Nations now marks as the International Day against Nuclear Tests.",
    "novaya": "An Arctic archipelago. Its small Nenets population was moved to the mainland when the test site was set up in the mid 1950s (Khalturin et al. 2005). Tsar Bomba and almost all of the largest Soviet tests were fired here: {{nz.pct_ussr_yield|pc}} of all Soviet test yield.",
    "kapustin": "A missile range near the Volga, used for rocket-carried and high altitude tests from 1957 to 1962.",
    "azgir": "Peaceful explosions in salt domes in western Kazakhstan, to make underground cavities.",
    "ussrpne": "Peaceful nuclear explosions across Russia, Kazakhstan, Ukraine, Uzbekistan and Turkmenistan, for seismic surveys, gas and oil work and underground cavities, and a 1954 military exercise in the Orenburg region (SIPRI purposes).",
    "lopnur": "China's only test site, in the desert of Xinjiang, used from {{site.lopnur.y0|raw}} to {{site.lopnur.y1|raw}}: {{site.lopnur.atm|int}} tests in the atmosphere, the last in 1980, then underground (Wikipedia).",
    "reggane": "In the Algerian Sahara, then under French colonial rule and during the Algerian war of independence: France's first four tests, in the atmosphere, 1960 and 1961 (Wikipedia).",
    "inekker": "Underground tests in the Hoggar mountains of the Algerian Sahara, 1961 to 1966. {{algeria.inekker_after|int}} of the {{site.inekker.n|int}} took place after Algeria became independent on 5 July 1962, under the Evian Accords.",
    "moruroa": "An atoll in French Polynesia, then a French overseas territory: {{site.moruroa.n|int}} tests from {{site.moruroa.y0|raw}} to {{site.moruroa.y1|raw}}, in the atmosphere until {{polynesia.last_atm_year|raw}}, then underground (Wikipedia). In 2010 France passed a law to compensate people made ill by its tests.",
    "fangataufa": "Moruroa's neighbouring atoll in French Polynesia: France's first hydrogen bomb, Canopus, in 1968, and its last test, in January 1996 (Wikipedia).",
    "montebello": "Uninhabited islands off Western Australia: Britain's first atomic test, Hurricane, in 1952, fired in a ship (Wikipedia).",
    "emu": "Two British tests in the South Australian desert in 1953, on the lands of Anangu Aboriginal people (Royal Commission 1985).",
    "maralinga": "Seven British tests in 1956 and 1957 on the traditional lands of the Maralinga Tjarutja, an Anangu people. A Royal Commission reported on the British tests and their effects on Aboriginal people in 1985; the last of the test lands were handed back to the Maralinga Tjarutja in 2014.",
    "pokhran": "India's test range in the Thar Desert of Rajasthan: Smiling Buddha in 1974 and the five devices of Pokhran-II in 1998. The range itself is uninhabited, but houses in villages within five kilometres were damaged (Wikipedia).",
    "chagai": "Chagai-I, Pakistan's first tests: five devices fired together inside a mountain in the Ras Koh Hills of Balochistan on 28 May 1998 (Wikipedia).",
    "kharan": "Chagai-II, Pakistan's second test, in the Kharan Desert of Balochistan on 30 May 1998 (Wikipedia).",
    "punggye": "North Korea's six tests, 2006 to 2017, all underground in tunnels at Punggye-ri in the mountains of the north east. Yields are estimates, given as ranges (Wikipedia).",
    "hiroshima": "The bomb dropped on Hiroshima on 6 August 1945. Wartime use, not a test: shown for reference and not counted.",
    "nagasaki": "The bomb dropped on Nagasaki on 9 August 1945. Wartime use, not a test: shown for reference and not counted.",
}

# ---------- facts stated in words (page, site notes) ----------
T = pd.read_csv(f"{DATA}/tests.csv", keep_default_na=False, na_values=[""])
TT = T[T.is_test == 1]
S = R["site"]; C = R["c"]
assert R["peak_year"] == 1962 and R["peak_by_country"]["US"] + R["peak_by_country"]["USSR"] + R["peak_by_country"]["France"] + R["peak_by_country"]["UK"] == R["peak_n"]
assert R["n_1959"] == 0 and (TT[TT.year == 1960].country == "France").all()                     # "all of them French"
assert int((TT[TT.year < 1951]).shape[0]) <= 8                                                    # "only a handful before 1951"
assert C["USSR"]["first_year"] == 1949 and C["UK"]["first_year"] == 1952
s61 = TT[(TT.country == "Soviet Union") & (TT.year == 1961)].date.min()
assert s61.startswith("1961-09")                                                                  # "broke the pause in September 1961"
assert C["France"]["last_atm_year"] == 1974 and C["China"]["last_atm_year"] == 1980 and R["last_atm"]["country"] == "China"
assert R["post_atm_fr"] == R["polynesia"]["atm"]                                                  # "all in French Polynesia"
assert TT[(TT.country == "China")].site_key.eq("lopnur").all()
assert R["top_site_yield"] == "novaya" and R["site_rank_n"][0] == "nevada"
assert C["France"]["outside_home"] == C["France"]["n"] and C["UK"]["outside_home"] == C["UK"]["n"]
assert R["away_by_country"]["USSR"] == 0 and R["away_by_country"]["China"] == 0
assert R["kiribati"]["uk"] == S["kiritimati"]["by_country"][3] + S["malden"]["by_country"][3]
assert C["US"]["last_year"] == 1992 and C["USSR"]["last_year"] == 1990 and C["UK"]["last_year"] == 1991 and C["France"]["last"].endswith("January 1996") and C["China"]["last"].endswith("July 1996")
assert R["nk"]["tests"][0]["note"].startswith("Possibly a fizzle") and "hydrogen bomb" in R["nk"]["tests"][5]["note"]
assert TT[TT.country == "North Korea"].environment.eq("Underground").all()
assert R["kinds"][0]["pct"] > 80                                                                     # "most tests were on own territory"
assert R["top20_ussr"] + R["top20_us"] == 20
assert R["sep27_1962"]["hi"] == 50000                                                                  # range note in the paper
# site notes
assert S["johnston"]["y0"] == 1958 and S["johnston"]["y1"] == 1962
assert S["kapustin"]["y0"] == 1957 and S["kapustin"]["y1"] == 1962
assert S["reggane"]["n"] == 4 and S["reggane"]["atm"] == 4 and S["reggane"]["y1"] == 1961
assert S["inekker"]["ug"] == S["inekker"]["n"] and S["inekker"]["y0"] == 1961 and S["inekker"]["y1"] == 1966
assert S["emu"]["n"] == 2 and S["emu"]["y0"] == 1953 and S["maralinga"]["n"] == 7 and (S["maralinga"]["y0"], S["maralinga"]["y1"]) == (1956, 1957)
assert S["montebello"]["y0"] == 1952 and TT[(TT.site_key == "montebello") & (TT.year == 1952)].deployment_code.eq("SHIP").all()
assert S["amchitka"]["n"] == 3 and S["malden"]["n"] == 3 and S["malden"]["y0"] == S["malden"]["y1"] == 1957
assert S["kiritimati"]["by_country"][0] == 24 and TT[(TT.site_key == "kiritimati") & (TT.country == "United States")].year.eq(1962).all()
assert TT[(TT.site_key == "kiritimati") & (TT.country == "United States")].deployment_code.eq("AIRDROP").all()
assert set(TT[(TT.site_key == "kiritimati") & (TT.country == "United Kingdom")].year) == {1957, 1958}
fa = TT[TT.site_key == "fangataufa"]
assert fa[fa["name"] == "Canopus"].year.iloc[0] == 1968 and fa.date.max() == "1996-01-27"
assert TT[(TT.site_key == "trinity")].date.iloc[0] == "1945-07-16"
assert TT[TT["name"] == "Ivy Mike"].site_key.iloc[0] == "enewetak"
assert TT[TT["name"] == "Cannikin"].year.iloc[0] == 1971 and TT[TT["name"] == "Cannikin"].site_key.iloc[0] == "amchitka"
assert TT[TT.site_key == "ocean"].year.isin([1955, 1958, 1962]).all()
assert set(TT[TT.site_key == "usmain"].purpose_code) <= {"PNE:PLO", "PNE:V", "PNE", "WR/PNE", "PNE/WR"}, set(TT[TT.site_key == "usmain"].purpose_code)
up = TT[TT.site_key == "ussrpne"]
assert (up.purpose_code.str.startswith("PNE")).sum() >= len(up) - 2 and (up.purpose_code == "ME").sum() == 1
assert (TT[TT.site_key == "azgir"].purpose_code.str.startswith("PNE")).all()
assert "Rongelap and Rongerik" in WIKI["bravo"] and "Kiritimati" in WIKI["uk"]
assert "Daigo Fukury" in json.dumps(jload(f"{RAW}/wiki_List_of_nuclear_weapons_tests.json"), ensure_ascii=False)


def notes():
    out = {k: fill(v, R) for k, v in NOTES.items()}
    for k in SKEY:
        assert k in out, k
    return out


def build():
    html = fill(open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read(), R)
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITEJ)).replace("/*NOTES*/", J(notes()))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    left = re.findall(r"\{\{[^}]*\}\}", html)
    assert set(left) <= {"10.5281/zenodo.23857489", "https://blog.tristanhotham.com/2026/10/31/nuclear-tests/"}, set(left)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    jsave(notes(), f"{DATA}/site_notes.json", indent=1)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
