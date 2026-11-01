"""Clean the SIPRI list of explosions (1945 to 1998), assign sites, environments and central yields, add names of the
largest Soviet and Chinese tests and of the Indian and Pakistani tests from Wikipedia, and add North Korea's six tests
(2006 to 2017) from the Wikipedia list of North Korean tests (dates, positions and yield ranges from the page only).
Writes data/tests.csv and WORK/wiki.json (sentences quoted from the pages for checking)."""
import bs4
import pandas as pd
from common import *


def page(name):
    j = jload(f"{RAW}/wiki_{name}.json")
    s = bs4.BeautifulSoup(j["html"], "html.parser")
    for x in s.find_all(["sup", "style"]):
        x.decompose()
    assert j["revid"] == WIKI_REV[j["title"]], (j["title"], j["revid"])
    return j["title"], s


def text(s):
    return re.sub(r"\s+", " ", s.get_text(" ", strip=True))


D = pd.read_csv(f"{RAW}/nuclear_explosions.csv")
n_raw = len(D)
assert n_raw == 2051
D["region"] = D.region.str.strip()
D["site"] = D.region.map(REGION_SITE).fillna("ussrpne")
assert (D.loc[D.site == "ussrpne", "country"] == "USSR").all()
D["env"] = D["type"].str.strip().map(ENV_OF)
assert D.env.notna().all(), D.loc[D.env.isna(), "type"].unique()
D["approx_pos"] = 0
zero = (D.latitude == 0) & (D.longitude == 0)
med = D[~zero].groupby("region")[["latitude", "longitude"]].median()
for i in D.index[zero]:
    code = D.at[i, "region"]
    if code in FIX_POS:
        la, lo, where = FIX_POS[code]
    else:
        la, lo = med.loc[POS_ALIAS.get(code, code)]
        where = "the other records with site code " + POS_ALIAS.get(code, code)
    D.loc[i, ["latitude", "longitude", "approx_pos"]] = [round(la, 3), round(lo, 3), 1]
    D.at[i, "where"] = where
print("positions filled", int(zero.sum()))
assert not ((D.latitude == 0) & (D.longitude == 0)).any()

# yields: the source gives a lower and an upper estimate in kilotons; "0 to 20" means "less than 20 kt".
D["yield_lo"] = D.yield_lower.where(D.yield_lower.notna(), D.yield_upper)
D["yield_hi"] = D.yield_upper.where(D.yield_upper.notna(), D.yield_lower)
D["yield_mid"] = (D.yield_lo + D.yield_hi) / 2
D["name"] = D.name.fillna("").str.strip().str.title().replace({"Littleboy": "Little Boy", "Fatman": "Fat Man"})
D["name_source"] = np.where(D.name != "", "SIPRI", "")
D["country_i"] = D.country.map(C_OF)
D["date"] = D.date_long.astype(int)

# ---------- names from Wikipedia: the most powerful tests (tables of the list page) ----------
title, S = page("List_of_nuclear_weapons_tests")
WT = []
for tab in S.find_all("table", class_="wikitable"):
    head = [c.get_text(" ", strip=True) for c in tab.find("tr").find_all(["th", "td"])]
    if not head or not head[0].startswith("Date"):
        continue
    mult = 1000 if "megaton" in head[1] else 1
    for tr in tab.find_all("tr")[1:]:
        c = [x.get_text(" ", strip=True) for x in tr.find_all(["td", "th"])]
        if len(c) < 6:
            continue
        dt = pd.to_datetime(c[0].replace(".", ","), format="%B %d, %Y")
        WT.append((dt, c[3], c[5], float(c[1].replace(",", "")) * mult))
CMAP = {"Soviet Union": "USSR", "USA": "USA", "United States": "USA", "China": "CHINA", "UK": "UK", "United Kingdom": "UK", "France": "FRANCE"}
DT = pd.to_datetime(D.date.astype(str), format="%Y%m%d")
named = 0
for dt, cn, nm, y in WT:
    # same state, within a day (Wikipedia gives GMT; SIPRI sometimes the local date), yield within a factor of 1.5
    m = (abs((DT - dt).dt.days) <= 1) & (D.country == CMAP[cn]) & (D.yield_lo <= y * 1.5) & (D.yield_hi >= y / 1.5)
    if m.sum() != 1:
        continue
    old = D.loc[m, "name"].iloc[0]; nm = dash(nm).replace(" , ", ", ").replace("Test #", "Soviet test no. ")
    if old == "" or (old.lower() in nm.lower() and "(" not in nm and len(nm) > len(old)):   # e.g. "Bravo" -> "Castle Bravo"
        D.loc[m, ["name", "name_source"]] = [nm, "Wikipedia" if old == "" else "SIPRI and Wikipedia"]
        named += 1
tsar = D[(D.date == 19611030) & (D.country == "USSR") & (D.yield_hi > 1000)]
assert len(tsar) == 1 and tsar["name"].iloc[0].startswith("Tsar Bomba") and tsar.yield_hi.iloc[0] == 50000, tsar
bravo = D[(D.date == 19540228) & (D["name"] == "Castle Bravo")]
assert len(bravo) == 1 and bravo.yield_hi.iloc[0] == 15000      # SIPRI dates Castle Bravo 28 February (local 1 March)
TX = text(S)
WIKI = {"list_title": title,
        "ctbt": re.search(r"As a result of the 1996 Comprehensive Nuclear-Test-Ban Treaty[^.]*\.", TX).group(0),
        "ptbt": re.search(r"Since 1963 the great majority have been underground due to the Partial Test Ban Treaty \.", TX).group(0).replace(" .", "."),
        "bravo": re.search(r"The unanticipated yield[^.]*\.[^.]*\.", TX).group(0),
        "algeria": re.search(r"Four were tested at Reggane[^.]*\.", TX).group(0),
        "uk": re.search(r"The United Kingdom has conducted 45 tests[^.]*\.", TX).group(0),
        "china": re.search(r"The People's Republic of China conducted 45 tests[^)]*\)", TX).group(0)}
assert "Rongelap and Rongerik" in WIKI["bravo"] and "evacuated" in WIKI["bravo"]
assert "French Algeria" in WIKI["algeria"] and "French Polynesia" in WIKI["algeria"]
assert "Maralinga" in WIKI["uk"] and "Kiritimati" in WIKI["uk"]
# totals table, for the comparison of counts in the paper
tot = {}
for tab in S.find_all("table", class_="wikitable"):
    rows = tab.find_all("tr")
    if rows and rows[0].get_text(" ", strip=True).startswith("Country Tests"):
        for tr in rows[1:]:
            c = [x.get_text(" ", strip=True) for x in tr.find_all(["td", "th"])]
            tot[re.sub(r"\s*\[.*", "", c[0]).strip()] = {"tests": int(c[1].replace(",", "")), "total_kt": float(c[7].replace(",", ""))}
WIKI["totals"] = tot
assert tot["Total"]["tests"] == 2121 and tot["North Korea"]["tests"] == 6

# ---------- India and Pakistan: names from the Pokhran-II and Chagai-I pages ----------
_, P2 = page("Pokhran_II"); T2 = text(P2)
_, C1 = page("Chagai_I"); T1 = text(C1)
assert "code name Smiling Buddha" in T2 and "11 and 13 May 1998" in T1 and "Chagai-I on 28 May 1998 and Chagai-II on 30 May 1998" in T2
assert "Group-I: Shakti I" in T2 and "Group-II: Shakti IV" in T2
NAMES = {(19740518, "INDIA"): "Smiling Buddha (Pokhran-I)", (19980511, "INDIA"): "Shakti I, II and III (Pokhran-II)",
         (19980513, "INDIA"): "Shakti IV and V (Pokhran-II)", (19980528, "PAKIST"): "Chagai-I", (19980530, "PAKIST"): "Chagai-II"}
for (dt, c), nm in NAMES.items():
    m = (D.date == dt) & (D.country == c)
    assert m.sum() == 1
    D.loc[m, ["name", "name_source"]] = [nm, "Wikipedia"]
WIKI["chagai_yield"] = re.search(r"independent and non-government sanctioned organizations puts the figure at the possible 15[^ ]*20 kt range", T1).group(0)
WIKI["pokhran_villages"] = re.search(r"Though the test was carried out in an uninhabited area[^.]*\.", T2).group(0)

# ---------- North Korea, 2006 to 2017: from the Wikipedia list of North Korean tests ----------
_, NK = page("List_of_nuclear_weapons_tests_of_North_Korea")
tab = [t for t in NK.find_all("table", class_="wikitable") if t.find("tr").get_text(" ", strip=True).startswith("Sequence")][0]
trs = tab.find_all("tr")[1:]
nk = []
for i, tr in enumerate(trs):
    c = [x.get_text(" ", strip=True) for x in tr.find_all(["td", "th"])]
    if not re.match(r"\(\d\)", c[0]):
        continue
    dt = pd.to_datetime(" ".join(c[1].split()[:3]), format="%d %B %Y")
    m = re.search(r"([\d.]+)°N ([\d.]+)°E", c[3].replace("﻿", ""))
    y = re.match(r"([\d.]+)\s*[–-]\s*([\d.]+)\s*kt", c[6])
    note = ""
    nxt = trs[i + 1] if i + 1 < len(trs) else None
    if nxt is not None:
        nc = [x.get_text(" ", strip=True) for x in nxt.find_all(["td", "th"])]
        if len(nc) == 1:
            note = re.split(r"(?<=\.)\s", nc[0])[0]
            note = re.sub(r"\s+([.,)])", r"\1", note.replace("\xa0", " "))
    nk.append({"date": int(dt.strftime("%Y%m%d")), "lat": float(m.group(1)), "lon": float(m.group(2)),
               "lo": float(y.group(1)), "hi": float(y.group(2)), "delivery": c[5], "note": dash(note), "raw_yield": dash(c[6])})
assert [x["date"] for x in nk] == [20061009, 20090525, 20130212, 20160106, 20160909, 20170903], nk
assert [(x["lo"], x["hi"]) for x in nk] == [(0.7, 2), (2, 5.4), (6, 16), (7, 16.5), (15, 25), (70, 280)]
NKN = ["2006 test", "2009 test", "2013 test", "January 2016 test", "September 2016 test", "2017 test"]
rows = []
for k, x in enumerate(nk):
    rows.append({"date": x["date"], "year": x["date"] // 10000, "id_no": 900001 + k, "country": "NKOREA", "region": "PUNGGYE-RI",
                 "source": "Wikipedia", "latitude": x["lat"], "longitude": x["lon"], "magnitude_body": np.nan, "magnitude_surface": np.nan,
                 "depth": np.nan, "yield_lo": x["lo"], "yield_hi": x["hi"], "yield_mid": (x["lo"] + x["hi"]) / 2, "purpose": "WR",
                 "name": NKN[k], "name_source": "Wikipedia", "type": "UG", "site": "punggye", "env": 2, "approx_pos": 0,
                 "country_i": 7, "note": x["note"]})
WIKI["nk"] = nk
NKD = pd.DataFrame(rows)
D["note"] = ""
D.loc[D.approx_pos == 1, "note"] = "No position in the source: placed approximately, at " + D.loc[D.approx_pos == 1, "where"] + "."
A = pd.concat([D, NKD], ignore_index=True)
A["year"] = A.date // 10000
A["test"] = (A.purpose != "COMBAT").astype(int)
out = pd.DataFrame({
    "id": A.id_no.astype(int), "date": A.date.map(ymd), "year": A.year, "country": [COUNTRIES[i][0] for i in A.country_i],
    "site": [SITES[SI[s]][1] for s in A.site], "site_key": A.site, "source_site_code": A.region, "lat": A.latitude.round(4),
    "lon": A.longitude.round(4), "position_approximate": A.approx_pos.astype(int),
    "environment": [ENVS[int(e)][0] for e in A.env], "deployment": A["type"].str.strip().map(TYPE_NAME),
    "deployment_code": A["type"].str.strip(), "purpose": A.purpose.map(lambda p: PURPOSE_NAME.get(p, p)), "purpose_code": A.purpose,
    "is_test": A.test, "yield_kt_low": A.yield_lo, "yield_kt_high": A.yield_hi, "yield_kt_mid": A.yield_mid,
    "body_wave_magnitude": A.magnitude_body.replace(0, np.nan), "surface_wave_magnitude": A.magnitude_surface.replace(0, np.nan),
    "depth_km": A.depth, "name": A.name, "name_source": A.name_source, "record_source": np.where(A.country == "NKOREA", "Wikipedia",
    "SIPRI (Bergkvist and Ferm 2000); reporting agency " + A.source.astype(str)), "note": A.note})
out.to_csv(f"{DATA}/tests.csv", index=False)
jsave(WIKI, f"{WORK}/wiki.json", indent=1)
print("records", len(out), "of which tests", int(out.is_test.sum()), "; SIPRI", n_raw, "+ North Korea", len(NKD), "; names from Wikipedia", named)
print(out.groupby("country").size().to_dict())
print(out.groupby("site").size().sort_values().tail(12).to_dict())
