"""Every number quoted anywhere (page, paper, blog, collage, post) goes into data/results.json. Also writes the page data
(data/site.json, data/points.json) and tidy tables (data/tests_by_year_country.csv, data/sites.csv, data/countries.csv)."""
import pandas as pd
from common import *

D = pd.read_csv(f"{DATA}/tests.csv", keep_default_na=False, na_values=[""])
D["name"] = D["name"].fillna(""); D["note"] = D["note"].fillna(""); D["purpose"] = D["purpose"].fillna("not recorded")
D["ci"] = D.country.map({c[0]: i for i, c in enumerate(COUNTRIES)})
D["ei"] = D.environment.map({e[0]: i for i, e in enumerate(ENVS)})
D["si"] = D.site_key.map(SI)
D["d"] = D.date.str.replace("-", "").astype(int)
D["kind"] = [KIND_GUEST.get((c, k), SITES[SI[k]][3]) for c, k in zip(D.country, D.site_key)]
D["island"] = D.site_key.map(lambda k: SITES[SI[k]][4])
T = D[D.is_test == 1].copy()          # tests only: Hiroshima and Nagasaki are kept in the data but are not tests
W = D[D.is_test == 0]
YEARS = list(range(1945, 2018))
N = len(T)
pc = lambda a, b: 100.0 * a / b
R = {"meta": {"page": PAGE, "repo": REPO, "slug": SLUG, "retrieved": "2026", "wiki_revisions": WIKI_REV}}
WIKI = jload(f"{WORK}/wiki.json")

# ---------- totals ----------
R["n_records"] = len(D); R["n"] = N; R["n_sipri"] = int((D.record_source != "Wikipedia").sum()); R["n_nk"] = int((D.country == "North Korea").sum())
R["n_sipri_tests"] = int(((D.record_source != "Wikipedia") & (D.is_test == 1)).sum())
R["n_wartime"] = len(W)
R["n_countries"] = int(T.country.nunique())
R["first"] = {"date": longdate(T.d.min()), "name": T.loc[T.d.idxmin(), "name"]}
R["last"] = {"date": longdate(T.d.max()), "country": T.loc[T.d.idxmax(), "country"]}
R["n_sites"] = int(T.site_key.nunique())
R["n_positions"] = int(T[["lat", "lon"]].drop_duplicates().shape[0])
R["n_approx_pos"] = int(T.position_approximate.sum())
R["yield_total_mid"] = float(T.yield_kt_mid.sum()); R["yield_total_lo"] = float(T.yield_kt_low.sum()); R["yield_total_hi"] = float(T.yield_kt_high.sum())
R["n_yield_unknown"] = int(T.yield_kt_mid.isna().sum())
R["n_range_0"] = int(((T.yield_kt_low == 0) & (T.yield_kt_high > 0)).sum())     # "less than x kt"
R["hiroshima_kt"] = float(W.loc[W.site_key == "hiroshima", "yield_kt_mid"].iloc[0])
R["nagasaki_kt"] = float(W.loc[W.site_key == "nagasaki", "yield_kt_mid"].iloc[0])
R["total_in_hiroshimas"] = R["yield_total_mid"] / R["hiroshima_kt"]

# ---------- years ----------
YC = pd.crosstab(T.year, T.ci).reindex(index=YEARS, columns=range(len(COUNTRIES)), fill_value=0)
YE = pd.crosstab(T.year, T.ei).reindex(index=YEARS, columns=range(len(ENVS)), fill_value=0)
YY = T.groupby(["year", "ci"]).yield_kt_mid.sum().unstack(fill_value=0).reindex(index=YEARS, columns=range(len(COUNTRIES)), fill_value=0)
by_year = YC.sum(axis=1)
R["years"] = [[y] + [int(v) for v in YC.loc[y]] for y in YEARS]
R["years_env"] = [[y] + [int(v) for v in YE.loc[y]] for y in YEARS]
R["years_yield"] = [[y] + [round(float(v), 1) for v in YY.loc[y]] for y in YEARS]
R["by_year"] = {str(y): int(by_year[y]) for y in YEARS}
R["peak_year"] = int(by_year.idxmax()); R["peak_n"] = int(by_year.max())
assert R["peak_year"] == 1962
R["peak_by_country"] = {CSHORT[i]: int(YC.loc[1962, i]) for i in range(len(COUNTRIES))}
R["peak_days_per_test"] = 365 / R["peak_n"]
R["peak_atm"] = int(YE.loc[1962, 0] + YE.loc[1962, 1])
R["n_1958"] = int(by_year[1958]); R["n_1959"] = int(by_year[1959]); R["n_1960"] = int(by_year[1960]); R["n_1961"] = int(by_year[1961])
R["yield_1962"] = float(YY.loc[1962].sum()); R["yield_1961"] = float(YY.loc[1961].sum())
R["yield_61_62_pct"] = pc(R["yield_1961"] + R["yield_1962"], R["yield_total_mid"])
R["n_years_zero"] = [y for y in YEARS if by_year[y] == 0 and y <= 1998]
R["n_1945_62"] = int(by_year.loc[1945:1962].sum())
R["n_1963_92"] = int(by_year.loc[1963:1992].sum())
R["avg_1963_92"] = R["n_1963_92"] / 30
R["n_after_1992"] = int(by_year.loc[1993:].sum())
R["n_1990s"] = int(by_year.loc[1990:1999].sum())
R["max_after_1963"] = int(by_year.loc[1964:].max()); R["max_after_1963_year"] = int(by_year.loc[1964:].idxmax())

# ---------- countries ----------
cs = []
for i, (name, col) in enumerate(COUNTRIES):
    s = T[T.ci == i]
    big = s.loc[s.yield_kt_mid.idxmax()]
    cs.append({"name": name, "short": CSHORT[i], "n": int(len(s)), "pct": pc(len(s), N),
               "first": longdate(s.d.min()), "first_year": int(s.year.min()), "last": longdate(s.d.max()), "last_year": int(s.year.max()),
               "atm": int((s.ei == 0).sum()), "uw": int((s.ei == 1).sum()), "ug": int((s.ei == 2).sum()),
               "atm_after_ptbt": int(((s.ei < 2) & (s.d > PTBT_DATE)).sum()),
               "last_atm": longdate(s.loc[s.ei < 2, "d"].max()) if (s.ei < 2).any() else "",
               "last_atm_year": int(s.loc[s.ei < 2, "year"].max()) if (s.ei < 2).any() else None,
               "yield_mid": float(s.yield_kt_mid.sum()), "yield_lo": float(s.yield_kt_low.sum()), "yield_hi": float(s.yield_kt_high.sum()),
               "yield_pct": pc(s.yield_kt_mid.sum(), T.yield_kt_mid.sum()),
               "biggest_kt": float(big.yield_kt_mid), "biggest_lo": float(big.yield_kt_low), "biggest_hi": float(big.yield_kt_high),
               "biggest_name": big["name"] or "unnamed", "biggest_date": longdate(big.d),
               "pne": int(s.purpose_code.str.startswith("PNE").sum()),
               "outside_home": int((s.kind.isin([1, 2])).sum()),
               "sites": int(s.site_key.nunique())})
R["countries"] = cs
CI = {c["short"]: c for c in cs}
R["c"] = {c["short"].replace(". ", ""): c for c in cs}
R["us_ussr_pct"] = pc(CI["US"]["n"] + CI["USSR"]["n"], N)
R["us_ussr_yield_pct"] = pc(CI["US"]["yield_mid"] + CI["USSR"]["yield_mid"], R["yield_total_mid"])
R["uk_at_nevada"] = int(((T.ci == 3) & (T.site_key == "nevada")).sum())
R["us_tests_excl_wartime"] = CI["US"]["n"]

# ---------- atmosphere to underground ----------
pre = T[T.d < PTBT_DATE]; post = T[T.d > PTBT_DATE]
R["env"] = [{"name": n, "n": int((T.ei == k).sum()), "pct": pc((T.ei == k).sum(), N), "yield_mid": float(T.loc[T.ei == k, "yield_kt_mid"].sum()),
             "yield_pct": pc(T.loc[T.ei == k, "yield_kt_mid"].sum(), R["yield_total_mid"])} for k, (n, c) in enumerate(ENVS)]
R["atm_total"] = int((T.ei < 2).sum())                                   # atmosphere, space and underwater: what the PTBT banned
R["atm_yield_pct"] = pc(T.loc[T.ei < 2, "yield_kt_mid"].sum(), R["yield_total_mid"])
R["pre_n"] = len(pre); R["post_n"] = len(post)
R["pre_atm_pct"] = pc((pre.ei < 2).sum(), len(pre)); R["post_ug_pct"] = pc((post.ei == 2).sum(), len(post))
R["post_atm"] = int((post.ei < 2).sum())
R["post_atm_fr"] = int(((post.ei < 2) & (post.ci == 2)).sum()); R["post_atm_cn"] = int(((post.ei < 2) & (post.ci == 4)).sum())
assert R["post_atm"] == R["post_atm_fr"] + R["post_atm_cn"]
R["last_atm"] = {"date": longdate(T.loc[T.ei < 2, "d"].max()), "country": T.loc[T.loc[T.ei < 2, "d"].idxmax(), "country"]}
R["pre_atm_n"] = int((pre.ei < 2).sum())
R["pre_atm_pct_of_all_atm"] = pc(R["pre_atm_n"], R["atm_total"])
R["ug_before_ptbt"] = int((pre.ei == 2).sum())
R["pre_by"] = [[int(((pre.ci == i) & (pre.ei == e)).sum()) for e in range(3)] for i in range(len(COUNTRIES))]
R["post_by"] = [[int(((post.ci == i) & (post.ei == e)).sum()) for e in range(3)] for i in range(len(COUNTRIES))]
R["first_ug"] = {"date": longdate(T.loc[T.ei == 2, "d"].min()), "name": T.loc[T.loc[T.ei == 2, "d"].idxmin(), "name"]}

# ---------- yield: sites, biggest tests, treaties ----------
ss = []
for k, (key, name, today, kind, isl) in enumerate(SITES):
    s = D[D.site_key == key]
    if not len(s):
        continue
    ss.append({"key": key, "name": name, "today": today, "kind": kind, "island": isl, "n": int(len(s)),
               "countries": sorted(s.country.unique().tolist(), key=lambda c: [x[0] for x in COUNTRIES].index(c)),
               "by_country": [int((s.ci == i).sum()) for i in range(len(COUNTRIES))],
               "y0": int(s.year.min()), "y1": int(s.year.max()), "atm": int((s.ei < 2).sum()), "ug": int((s.ei == 2).sum()),
               "yield_mid": float(s.yield_kt_mid.sum()), "yield_lo": float(s.yield_kt_low.sum()), "yield_hi": float(s.yield_kt_high.sum()),
               "yield_pct": pc(s.yield_kt_mid.sum(), R["yield_total_mid"]) if kind != 4 else 0,
               "max_kt": float(s.yield_kt_mid.max()), "lat": float(s.lat.median()), "lon": float(s.lon.median()),
               "bbox": [float(s.lat.min()), float(s.lon.min()), float(s.lat.max()), float(s.lon.max())]})
R["sites"] = ss
SS = {s["key"]: s for s in ss}
R["site"] = SS
order = sorted([s for s in ss if s["kind"] != 4], key=lambda s: -s["yield_mid"])
R["site_rank_yield"] = [s["key"] for s in order]
R["site_rank_n"] = [s["key"] for s in sorted([s for s in ss if s["kind"] != 4], key=lambda s: -s["n"])]
R["top_site_yield"] = order[0]["key"]
R["nz_yield_pct"] = SS["novaya"]["yield_pct"]
R["nevada_pct_n"] = pc(SS["nevada"]["n"], N)
R["groups"] = [{"name": g, "keys": ks, "n": sum(SS[k]["n"] for k in ks), "yield_mid": sum(SS[k]["yield_mid"] for k in ks),
                "bbox": [min(SS[k]["bbox"][0] for k in ks), min(SS[k]["bbox"][1] for k in ks), max(SS[k]["bbox"][2] for k in ks), max(SS[k]["bbox"][3] for k in ks)]}
               for g, ks in GROUPS]
G = {g["name"]: g for g in R["groups"]}

TB = T.sort_values(["yield_kt_mid", "d"], ascending=[False, True]).head(20)
R["biggest"] = [{"date": longdate(r.d), "year": int(r.year), "country": r.country, "site": r.site, "name": r["name"] or "unnamed",
                 "mid": float(r.yield_kt_mid), "lo": float(r.yield_kt_low), "hi": float(r.yield_kt_high), "env": int(r.ei)} for _, r in TB.iterrows()]
tsar = T[T["name"].str.startswith("Tsar Bomba")].iloc[0]; bravo = T[(T["name"] == "Castle Bravo") & (T.year == 1954)].iloc[0]
R["tsar"] = {"kt": float(tsar.yield_kt_mid), "date": longdate(tsar.d), "pct_total": pc(tsar.yield_kt_mid, R["yield_total_mid"]),
             "x_hiroshima": tsar.yield_kt_mid / R["hiroshima_kt"]}
R["bravo"] = {"kt": float(bravo.yield_kt_mid), "date_sipri": longdate(bravo.d), "x_hiroshima": bravo.yield_kt_mid / R["hiroshima_kt"]}
assert R["tsar"]["kt"] == 50000 and R["bravo"]["kt"] == 15000
assert R["biggest"][0]["name"].startswith("Tsar Bomba")
R["us_biggest_is_bravo"] = CI["US"]["biggest_name"] == "Castle Bravo"
assert R["us_biggest_is_bravo"]
top20 = TB.head(20)
R["top20_ussr"] = int((top20.ci == 1).sum()); R["top20_us"] = int((top20.ci == 0).sum())
R["top20_1961_62"] = int(top20.year.isin([1961, 1962]).sum())
R["mt_tests"] = int((T.yield_kt_mid >= 1000).sum())
R["mt_tests_yield_pct"] = pc(T.loc[T.yield_kt_mid >= 1000, "yield_kt_mid"].sum(), R["yield_total_mid"])
R["median_kt"] = float(T.yield_kt_mid.median())
R["under_20_pct"] = pc((T.yield_kt_high <= 20).sum(), T.yield_kt_high.notna().sum())
sep27 = T[(T.d == 19620927) & (T.ci == 1) & (T.yield_kt_high > 1000)].iloc[0]
R["sep27_1962"] = {"lo": float(sep27.yield_kt_low), "hi": float(sep27.yield_kt_high)}
cann = T[T["name"] == "Cannikin"].iloc[0]
R["cannikin"] = {"lo": float(cann.yield_kt_low), "hi": float(cann.yield_kt_high)}
R["ug_biggest"] = {"name": T.loc[T[T.ei == 2].yield_kt_high.idxmax(), "name"]}
# Threshold Test Ban Treaty: 150 kt limit observed from 31 March 1976
tt = T[(T.d >= 19760331) & (T.ci.isin([0, 1]))]
R["ttbt_n"] = len(tt); R["ttbt_max_mid"] = float(tt.yield_kt_mid.max()); R["ttbt_over150_mid"] = int((tt.yield_kt_mid > 150).sum())
R["ttbt_over150_hi"] = int((tt.yield_kt_high > 150).sum())

# ---------- whose land: kinds of territory, islands ----------
R["kinds"] = [{"name": KINDS[k], "n": int((T.kind == k).sum()), "pct": pc((T.kind == k).sum(), N),
               "yield_mid": float(T.loc[T.kind == k, "yield_kt_mid"].sum()), "yield_pct": pc(T.loc[T.kind == k, "yield_kt_mid"].sum(), R["yield_total_mid"]),
               "atm": int(((T.kind == k) & (T.ei < 2)).sum())} for k in range(4)]
away = T[T.kind.isin([1, 2])]
R["away_n"] = len(away); R["away_pct"] = pc(len(away), N)
R["away_yield_pct"] = pc(away.yield_kt_mid.sum(), R["yield_total_mid"])
R["away_atm"] = int((away.ei < 2).sum()); R["away_atm_pct_of_atm"] = pc(R["away_atm"], R["atm_total"])
R["away_by_country"] = {CSHORT[i]: int((away.ci == i).sum()) for i in range(len(COUNTRIES))}
R["fr_away_pct"] = pc(R["away_by_country"]["France"], CI["France"]["n"])
R["uk_away_pct"] = pc(R["away_by_country"]["UK"], CI["UK"]["n"])
R["uk_home"] = int(((T.ci == 3) & (T.kind == 0)).sum())
assert R["uk_home"] == 0
isl = T[T.island]
R["island_n"] = len(isl); R["island_pct"] = pc(len(isl), N)
R["island_yield"] = float(isl.yield_kt_mid.sum()); R["island_yield_pct"] = pc(isl.yield_kt_mid.sum(), R["yield_total_mid"])
R["island_atm"] = int((isl.ei < 2).sum()); R["island_atm_pct_of_atm"] = pc(R["island_atm"], R["atm_total"])
R["island_atm_yield_pct"] = pc(isl.loc[isl.ei < 2, "yield_kt_mid"].sum(), T.loc[T.ei < 2, "yield_kt_mid"].sum())
pac = T[T.site_key.isin(["bikini", "enewetak", "johnston", "kiritimati", "malden", "moruroa", "fangataufa"])]
R["pacific_n"] = len(pac); R["pacific_yield"] = float(pac.yield_kt_mid.sum()); R["pacific_yield_pct"] = pc(pac.yield_kt_mid.sum(), R["yield_total_mid"])
mi = T[T.site_key.isin(["bikini", "enewetak"])]
R["marshall"] = {"n": len(mi), "yield": float(mi.yield_kt_mid.sum()), "yield_pct": pc(mi.yield_kt_mid.sum(), R["yield_total_mid"]),
                 "pct_us_yield": pc(mi.yield_kt_mid.sum(), CI["US"]["yield_mid"]), "x_hiroshima": mi.yield_kt_mid.sum() / R["hiroshima_kt"],
                 "y0": int(mi.year.min()), "y1": int(mi.year.max())}
fp = T[T.site_key.isin(["moruroa", "fangataufa"])]
R["polynesia"] = {"n": len(fp), "pct_fr": pc(len(fp), CI["France"]["n"]), "atm": int((fp.ei < 2).sum()), "ug": int((fp.ei == 2).sum()),
                  "y0": int(fp.year.min()), "y1": int(fp.year.max()), "last_atm_year": int(fp.loc[fp.ei < 2, "year"].max())}
al = T[T.site_key.isin(["reggane", "inekker"])]
R["algeria"] = {"n": len(al), "atm": int((al.ei < 2).sum()), "ug": int((al.ei == 2).sum()), "after_indep": int((al.d > ALGERIA_INDEP).sum()),
                "inekker_after": int(((al.site_key == "inekker") & (al.d > ALGERIA_INDEP)).sum()), "y0": int(al.year.min()), "y1": int(al.year.max())}
au = T[T.site_key.isin(["montebello", "emu", "maralinga"])]
R["australia"] = {"n": len(au), "maralinga": SS["maralinga"]["n"], "emu": SS["emu"]["n"], "montebello": SS["montebello"]["n"],
                  "y0": int(au.year.min()), "y1": int(au.year.max()), "yield": float(au.yield_kt_mid.sum())}
ki = T[T.site_key.isin(["kiritimati", "malden"])]
R["kiribati"] = {"n": len(ki), "uk": int((ki.ci == 3).sum()), "us": int((ki.ci == 0).sum()), "yield": float(ki.yield_kt_mid.sum())}
R["semi"] = {"n": SS["semipalatinsk"]["n"], "atm": SS["semipalatinsk"]["atm"], "pct_ussr": pc(SS["semipalatinsk"]["n"], CI["USSR"]["n"]),
             "y0": SS["semipalatinsk"]["y0"], "y1": SS["semipalatinsk"]["y1"]}
R["nz"] = {"n": SS["novaya"]["n"], "atm": SS["novaya"]["atm"], "yield": SS["novaya"]["yield_mid"], "pct_ussr_yield": pc(SS["novaya"]["yield_mid"], CI["USSR"]["yield_mid"])}
R["nevada"] = {"n": SS["nevada"]["n"], "atm": SS["nevada"]["atm"], "pct_us": pc(SS["nevada"]["n"] - R["uk_at_nevada"], CI["US"]["n"])}
R["lopnur"] = {"n": SS["lopnur"]["n"], "atm": SS["lopnur"]["atm"]}
R["ussr_pne"] = {"n": CI["USSR"]["pne"], "sites_pne": int(T[(T.ci == 1) & T.purpose_code.str.startswith("PNE")].site_key.isin(["ussrpne", "azgir"]).sum())}

# ---------- after the CTBT ----------
post_ctbt = T[T.d > CTBT_DATE]
R["post_ctbt"] = {"n": len(post_ctbt), "by": {CSHORT[i].replace(". ", ""): int((post_ctbt.ci == i).sum()) for i in range(len(COUNTRIES)) if (post_ctbt.ci == i).any()}}
R["since_1999"] = int((T.year >= 1999).sum())
nk = T[T.ci == 7]
R["nk"] = {"n": len(nk), "lo": float(nk.yield_kt_low.sum()), "hi": float(nk.yield_kt_high.sum()), "mid": float(nk.yield_kt_mid.sum()),
           "big_lo": float(nk.yield_kt_low.max()), "big_hi": float(nk.yield_kt_high.max()), "first_lo": float(nk.yield_kt_low.iloc[0]),
           "first_hi": float(nk.yield_kt_high.iloc[0]), "big_x_hiroshima": nk.yield_kt_mid.max() / R["hiroshima_kt"],
           "tests": [{"date": longdate(r.d), "lo": float(r.yield_kt_low), "hi": float(r.yield_kt_high), "note": r.note} for _, r in nk.iterrows()]}
R["sa_1998"] = {"india": int(((T.ci == 5) & (T.year == 1998)).sum()), "pakistan": int(((T.ci == 6) & (T.year == 1998)).sum())}
R["wiki_totals"] = WIKI["totals"]
R["wiki_total_kt"] = WIKI["totals"]["Total"]["total_kt"]
R["wiki_tests"] = WIKI["totals"]["Total"]["tests"]
R["years_since_last"] = 2026 - 2017

# ---------- tidy tables ----------
pd.DataFrame(R["years"], columns=["year"] + [c[0] for c in COUNTRIES]).to_csv(f"{DATA}/tests_by_year_country.csv", index=False)
pd.DataFrame([{**{k: s[k] for k in ("key", "name", "today", "n", "y0", "y1", "atm", "ug")}, "kind_of_territory": KINDS[s["kind"]], "island": s["island"],
               "countries": "; ".join(s["countries"]), "yield_kt_mid": round(s["yield_mid"], 1), "yield_kt_low": round(s["yield_lo"], 1),
               "yield_kt_high": round(s["yield_hi"], 1), "lat": round(s["lat"], 3), "lon": round(s["lon"], 3)} for s in ss]).to_csv(f"{DATA}/sites.csv", index=False)
pd.DataFrame([{k: c[k] for k in ("name", "n", "first", "last", "atm", "uw", "ug", "yield_mid", "yield_lo", "yield_hi", "biggest_name", "biggest_kt", "pne", "outside_home")}
              for c in cs]).round(1).to_csv(f"{DATA}/countries.csv", index=False)

# ---------- page data: points, spread where many tests share one position ----------
SITEJ = {"countries": COUNTRIES, "cshort": CSHORT, "envs": ENVS, "kinds": KINDS, "treaties": TREATIES,
         "sites": [[s["key"], s["name"], s["today"], s["kind"], s["island"]] for s in [dict(zip(("key", "name", "today", "kind", "island"), x)) for x in SITES]],
         "type_name": TYPE_NAME}
CN = jload(f"{WORK}/countries.json"); SITEJ["cname"] = CN["cname"]; SITEJ["cpos"] = CN["cpos"]
jsave(SITEJ, f"{DATA}/site.json")
P = D.sort_values("d").reset_index(drop=True)
grp = P.groupby(["lat", "lon"]).cumcount(); cnt = P.groupby(["lat", "lon"]).lat.transform("size")
ga = np.pi * (3 - np.sqrt(5))
pts = []
for i, p in P.iterrows():
    la, lo = p.lat, p.lon
    if cnt[i] > 1:     # sunflower spread: disc radius grows with the number of tests at the position (about 0.012 degrees per sqrt test)
        k = grp[i]; r = 0.012 * np.sqrt(k + .5); a = k * ga
        la = la + r * np.sin(a); lo = lo + r * np.cos(a) / np.cos(np.radians(la))
    y = p.yield_kt_mid
    pts.append([round(la, 4), round(lo, 4), int(p.d), int(p.ci), int(p.ei), None if pd.isna(y) else round(float(y), 3),
                None if pd.isna(p.yield_kt_low) else round(float(p.yield_kt_low), 3), None if pd.isna(p.yield_kt_high) else round(float(p.yield_kt_high), 3),
                int(p.si), p["name"], p.deployment_code, p.purpose, int(p.is_test), round(p.lat, 3), round(p.lon, 3), p.note, int(p.id)])
jsave({"cols": ["lat_shown", "lon_shown", "date", "country", "environment", "yield_mid", "yield_low", "yield_high", "site", "name", "deployment",
                "purpose", "is_test", "lat", "lon", "note", "id"], "rows": pts}, f"{DATA}/points.json")
R["spread_max_deg"] = 0.012 * np.sqrt(int(cnt.max()))
jsave(R, f"{DATA}/results.json", indent=1)
show = {k: R[k] for k in ("n", "n_records", "peak_year", "peak_n", "peak_by_country", "yield_total_mid", "yield_total_lo", "yield_total_hi", "atm_total",
                          "pre_atm_pct", "post_ug_pct", "post_atm_fr", "post_atm_cn", "last_atm", "island_pct", "island_yield_pct", "away_n", "away_pct",
                          "away_yield_pct", "marshall", "algeria", "polynesia", "post_ctbt", "ttbt_max_mid", "ttbt_over150_hi", "mt_tests", "mt_tests_yield_pct",
                          "nz_yield_pct", "yield_61_62_pct", "total_in_hiroshimas", "tsar", "kinds", "n_approx_pos", "median_kt", "under_20_pct")}
print(json.dumps(show, indent=0, cls=NpEnc)[:4000])
for c in cs:
    print(c["short"], c["n"], round(c["yield_mid"]), round(c["yield_lo"]), round(c["yield_hi"]), c["atm"], c["ug"], c["biggest_name"], c["last"], c["outside_home"])
for f in ("points.json", "site.json", "results.json", "tests.csv"):
    print(f, os.path.getsize(f"{DATA}/{f}") // 1024, "KB")
