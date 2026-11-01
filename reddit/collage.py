"""r/dataisbeautiful collage for nuclear-tests: 2400 px wide, light background. Numbers from data/results.json.
A world map of every test (circles sized by the cube root of yield, coloured by country) with the main test sites
labelled on open sea, the tests per year by country with the treaties marked, the biggest tests and whose land they
were on. Every map label is checked: its box must not touch land, any test circle or another label, and its leader line
must not cross another label. The script stops if a check fails."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Circle
from shapely.geometry import shape, box as sbox, Point, LineString
from shapely.ops import unary_union, transform as stransform

R = jload(f"{DATA}/results.json")
D = tests(); T = D[D.is_test == 1].copy(); W = D[D.is_test == 0]
CI = {c[0]: i for i, c in enumerate(COUNTRIES)}; T["ci"] = T.country.map(CI)
BGc = "#F7F5F0"; SEAc = "#E8EEF1"; LANDc = "#DEDAD0"
HALO = [pe.withStroke(linewidth=4, foreground=SEAc)]
HALOP = [pe.withStroke(linewidth=4, foreground=BGc)]
S = R["site"]
mt = lambda v: f"{v / 1000:,.0f} Mt" if v >= 9500 else f"{v / 1000:,.1f} Mt" if v >= 950 else f"{v:,.0f} kt"

Hpx = 3880
fy = lambda px: 1 - px / Hpx
fh = lambda px: px / Hpx
fig = plt.figure(figsize=(12, Hpx / 200), dpi=200, facecolor=BGc)

# ---------- title ----------
fig.text(.045, fy(58), "Every nuclear test", fontproperties=DISP, fontsize=54, color=FG, va="top")
fig.text(.045 + .505, fy(58), "1945 to 2017", fontproperties=DISP, fontsize=54, color=HOT, va="top")
fig.text(.045, fy(226), f"{R['n']:,} nuclear tests by eight countries, from Trinity to North Korea. Each circle is one test, sized by the\n"
         f"cube root of its explosive yield (the way blast damage scales) and coloured by the country that fired it.",
         fontproperties=SERP, fontsize=15.5, color=FG, va="top", linespacing=1.45)

# ---------- stat strip ----------
stats = [(f"{R['n']:,}", "nuclear tests, 1945 to 2017,\nnot counting Hiroshima\nand Nagasaki", FG),
         (f"{R['peak_n']}", f"tests in {R['peak_year']}, the peak\nyear: one every\n{R['peak_days_per_test']:.0f} days", HOT),
         (f"{R['post_ug_pct']:.0f}%", "of tests were underground\nafter the 1963 Partial\nTest Ban Treaty", "#5B5F66"),
         (f"{R['island_yield_pct']:.0f}%", f"of all the explosive yield\nwas set off on islands\n({R['island_pct']:.0f}% of tests)", "#2E86AB")]
ST0 = 430
for k, (big, small, c) in enumerate(stats):
    x = .045 + k * .2283
    fig.add_artist(Rectangle((x, fy(ST0 + 240)), .2133, fh(240), transform=fig.transFigure, fc="#FFFEFA", ec="#D9D3C6", lw=1))
    fig.add_artist(Rectangle((x, fy(ST0 + 6)), .2133, fh(6), transform=fig.transFigure, fc=c, ec="none"))
    fig.text(x + .012, fy(ST0 + 22), big, fontproperties=DISP, fontsize=30, color=c, va="top")
    fig.text(x + .012, fy(ST0 + 104), small, fontsize=9.6, color=MUT, va="top", linespacing=1.3)

# ---------- map ----------
EXT = ext_of(-180, -48, 180, 84)
asp = (EXT[3] - EXT[2]) / (EXT[1] - EXT[0])
mw = .955; mh = mw * 12 * asp / (Hpx / 200)
top_map = 860
BAND = 118      # paper band above the map for labels of inland Asian sites (pixels)
ax = fig.add_axes([.0225, fy(top_map) - mh, mw, mh])
world(ax, EXT, land=LANDc, sea=SEAc, ec="#FFFFFF", lw=.4)
px_per_unit = (mw * 12 * 200) / (EXT[1] - EXT[0])           # map pixels per projected metre
SC = 1.0
rad_pt = lambda y: np.maximum(1.5, .9 * SC * np.cbrt(np.clip(np.nan_to_num(y, nan=1), .05, None)))
o = T.sort_values("yield_kt_mid", ascending=False)
X, Y = proj(o.lon.values, o.lat.values)
r = rad_pt(o.yield_kt_mid.values)
big = r > 10
cols = np.array([CCOL[i] for i in o.ci])
ax.scatter(X[big], Y[big], s=r[big] ** 2, c=cols[big], alpha=.26, lw=1.3, edgecolors=cols[big], zorder=5)
ax.scatter(X[~big], Y[~big], s=r[~big] ** 2, c=cols[~big], alpha=.78, lw=.35, edgecolors="white", zorder=6)
wx, wy = proj(W.lon.values, W.lat.values); wr = rad_pt(W.yield_kt_mid.values)
ax.scatter(wx, wy, s=wr ** 2, facecolors="none", edgecolors=FG, lw=1.6, zorder=7)
# circles as shapely discs in map units (radius in points -> pixels -> metres)
u_per_pt = (200 / 72) / px_per_unit
DISCS = unary_union([Point(a, b).buffer(rr / 2 * u_per_pt + 2 * u_per_pt) for a, b, rr in zip(np.r_[X, wx], np.r_[Y, wy], np.r_[r, wr])])
L50 = jload(f"{GEO}/ne_50m_land.geojson")
# land the labels must avoid: every Natural Earth land polygon, with no size threshold (the text boxes are also
# buffered by 25 km); atolls with tests are protected by the circle check as well
from shapely.geometry import Polygon as SP
parts = []
for f in L50["features"]:
    gm = shape(f["geometry"]); gs = gm.geoms if hasattr(gm, "geoms") else [gm]
    for pg in gs:
        q = stransform(lambda x, y, z=None: EE.transform(np.clip(x, -179.99, 179.99), np.clip(y, -89.9, 89.9)), pg).buffer(0)
        if q.area > 0:      # every land polygon, however small
            parts.append(q)
LANDP = unary_union(parts)

# label specs: (text lines, label anchor lon/lat, alignment, site keys for the leader target)
def g(keys):
    n = sum(S[k]["n"] for k in keys); y = sum(S[k]["yield_mid"] for k in keys)
    return n, y
LAB = [   # (lines, sites, anchor (lon, lat) or ("band", lon), alignment)
    (["Novaya Zemlya", "{n} tests · {y}"], ["novaya"], ("band", 2), "center"),
    (["Semipalatinsk", "{n} tests · {y}"], ["semipalatinsk"], ("band", 52), "center"),
    (["Lop Nur", "{n} tests · {y}"], ["lopnur"], ("band", 102), "center"),
    (["Punggye-ri", "{n} tests · {y}"], ["punggye"], ("band", 152), "center"),
    (["Nevada", "{n} tests · {y}"], ["nevada"], (-133, 41), "right"),
    (["Johnston Atoll", "{n} tests · {y}"], ["johnston"], (-176, 29), "left"),
    (["Kiritimati and Malden", "{n} tests · {y}"], ["kiritimati", "malden"], (-146, 1), "left"),
    (["Moruroa and Fangataufa", "{n} tests · {y}"], ["moruroa", "fangataufa"], (-150, -34), "left"),
    (["Bikini and", "Enewetak", "{n} tests", "{y}"], ["bikini", "enewetak"], (152, 30), "left"),
    (["Algerian Sahara", "{n} tests · {y}"], ["reggane", "inekker"], (-24, 26), "right"),
    (["Pokhran and Chagai", "{n} tests · {y}"], ["pokhran", "chagai", "kharan"], (57, -13.5), "left"),
    (["Maralinga, Emu Field", "and Montebello", "{n} tests · {y}"], ["montebello", "emu", "maralinga"], (100, -33), "right"),
]
fig.canvas.draw()
rend = fig.canvas.get_renderer()
inv = ax.transData.inverted()
boxes, placed, FAIL = [], [], []
for lines, keys, (lo, la), ha in LAB:
    n, y = g(keys)
    lines = [s.format(n=f"{n:,}", y=mt(y)) for s in lines]
    if lo == "band":
        x0 = proj(la, 0)[0]; y0 = EXT[3] + (BAND * .62) / Hpx / mh * (EXT[3] - EXT[2])
    else:
        x0, y0 = proj(lo, la)
    nl = 2 if lines[0] in ("Hiroshima and", "Bikini and") else 1
    lines = ["\n".join(lines[:nl])] + lines[nl:]
    t1 = ax.text(x0, y0, lines[0], linespacing=1.05, fontproperties=DISPB, fontsize=12.5, color=FG, ha=ha, va="bottom", zorder=9, path_effects=HALOP if lo == "band" else HALO, clip_on=False)
    rest = [ax.text(x0, y0, "\n".join(lines[1:]), fontsize=9.6, color=FG if keys[0] != "hiroshima" else MUT, ha=ha, va="top", zorder=9, path_effects=HALOP if lo == "band" else HALO, linespacing=1.25, clip_on=False)]
    fig.canvas.draw()
    bb = [a.get_window_extent(rend).transformed(inv) for a in [t1] + rest]
    bx = sbox(min(b.x0 for b in bb), min(b.y0 for b in bb), max(b.x1 for b in bb), max(b.y1 for b in bb)).buffer(25000)
    name = lines[0]
    bad = [w for w, hit in (("land", bx.intersects(LANDP)), ("circle", bx.intersects(DISCS))) if hit] + [n2 for b2, n2 in boxes if bx.intersects(b2)]
    if bad:
        FAIL.append((name, bad)); ax.plot(*bx.exterior.xy, color="red", lw=1, zorder=20)
    boxes.append((bx, name))
    # leader: from the label box edge to the nearest circle edge of the site cluster
    pts = [proj(S[k]["lon"], S[k]["lat"]) for k in keys]
    cx = np.mean([p[0] for p in pts]); cy = np.mean([p[1] for p in pts])
    tgt = Point(cx, cy)
    start = bx.exterior.interpolate(bx.exterior.project(tgt))
    dist = start.distance(tgt)
    if dist > 260000:
        rr = max(np.max(rad_pt(T.loc[T.site_key.isin(keys), "yield_kt_mid"].values)) if keys[0] not in ("hiroshima", "nagasaki") else 6, 4) / 2 * u_per_pt + 60000
        f = max(0, (dist - rr) / dist)
        end = (start.x + (cx - start.x) * f, start.y + (cy - start.y) * f)
        placed.append((LineString([start, end]), name))
for ln, name in placed:
    for b2, n2 in boxes:
        if n2 != name:
            if ln.intersects(b2): FAIL.append((name, "leader crosses " + n2))
    xs, ys = ln.xy
    ax.plot(xs, ys, color=FG, lw=.8, alpha=.75, zorder=8, solid_capstyle="round", clip_on=False)
ax.text(*proj(-35, -20), "Atlantic\nOcean", fontsize=10, color="#8A97A3", ha="center", va="center", style="italic", zorder=4, linespacing=1.1)
ax.text(*proj(-122, 12), "Pacific\nOcean", fontsize=10, color="#8A97A3", ha="center", va="center", style="italic", zorder=4, linespacing=1.1)
ax.text(*proj(82, -3), "Indian Ocean", fontsize=10, color="#8A97A3", ha="center", va="center", style="italic", zorder=4)
map_bottom = top_map + mh * Hpx

# ---------- legend under the map (an axes in pixel units, so circles stay round) ----------
ly = map_bottom + 30
LH = 200
lg = fig.add_axes([.045, fy(ly + LH), .91, fh(LH)]); lg.set_xlim(0, .91 * 2400); lg.set_ylim(LH, 0); lg.axis("off")
lg.text(0, 4, "Testing country", fontsize=10, color=MUT, va="top")
for k, (nm, c) in enumerate(COUNTRIES):
    xx = (k % 4) * 300; yy = 52 + (k // 4) * 40
    lg.add_patch(Circle((xx + 12, yy), 10, fc=c, ec="none")); lg.text(xx + 32, yy, nm, fontsize=10.5, color=FG, va="center")
lg.add_patch(Circle((12, 140), 10, fc="none", ec=FG, lw=1.6))
lg.text(32, 140, "Hiroshima and Nagasaki, August 1945 (wartime use, not tests)", fontsize=10.5, color=FG, va="center")
lg.text(1290, 4, "Explosive yield (circle size)", fontsize=10, color=MUT, va="top")
for (v, t), xc in zip(((1, "1 kt"), (100, "100 kt"), (1000, "1 Mt"), (15000, "15 Mt"), (50000, "50 Mt")), (1320, 1420, 1530, 1660, 1830)):
    rp = float(rad_pt(np.array([v]))[0]) / 2 * 200 / 72
    lg.add_patch(Circle((xc, 140 - rp), rp, fc="none", ec=FG, lw=1))
    lg.text(xc, 168, t, fontsize=9.5, ha="center", va="center", color=FG)

# ---------- timeline ----------
tt = ly + LH + 40
fig.text(.045, fy(tt), "Tests per year, by country, and the treaties", fontproperties=DISP, fontsize=24, color=FG, va="top")
tax = fig.add_axes([.075, fy(tt + 720), .9, fh(620)]); tax.set_facecolor(BGc)
Yr = np.array(R["years"]); bottom = np.zeros(len(Yr))
for j in range(1, Yr.shape[1]):
    tax.bar(Yr[:, 0], Yr[:, j], bottom=bottom, color=CCOL[j - 1], width=.84, lw=0, zorder=2); bottom += Yr[:, j]
tax.set_ylim(0, 215); tax.set_xlim(1944.2, 2017.8)
tax.axvspan(1958.84, 1961.67, color="#E5E0D4", zorder=0, lw=0)
tax.text(1960.25, 207, "testing\npause", ha="center", va="top", fontsize=9.5, color=MUT, linespacing=1.05)
for x, t, yy in ((1963.6, "Partial Test Ban Treaty, Aug 1963:\nno tests in the air, space or water", 207),
                 (1974.5, "Threshold Test Ban Treaty, 1974:\nUS and Soviet tests up to 150 kt", 179),
                 (1996.73, "Comprehensive Test-Ban Treaty\nopened for signature, Sep 1996", 207)):
    tax.axvline(x, color=FG, lw=1, ls=(0, (3, 3)), alpha=.75, zorder=3)
    tax.text(x + .6, yy, t, fontsize=10, color=FG, va="top", zorder=4, linespacing=1.25, path_effects=HALOP)
tax.text(1961.5, R["peak_n"] + 2, f"{R['peak_n']} tests\nin {R['peak_year']}", ha="right", va="top", fontsize=11.5, fontweight="medium", path_effects=HALOP, zorder=5)
tax.text(1999.2, 52, "India and Pakistan, 1998;\nNorth Korea, 2006 to 2017", fontsize=10, color=FG, va="bottom", path_effects=HALOP)
tax.annotate("", xy=(1998, 6), xytext=(2001.5, 50), arrowprops=dict(arrowstyle="-", color=FG, lw=.8))
tax.annotate("", xy=(2011.5, 4), xytext=(2008.5, 50), arrowprops=dict(arrowstyle="-", color=FG, lw=.8))
tax.text(1975.6, 147, f"Before 1963, {R['pre_atm_pct']:.0f}% of tests\nwere in the open air or\nunderwater; after it, {R['post_ug_pct']:.0f}%\nwere underground.",
         fontsize=10, color=MUT, va="top", linespacing=1.35, path_effects=HALOP)
spines(tax); tax.grid(axis="y", color=RULE, lw=.8, zorder=0); tax.set_axisbelow(True); tax.tick_params(labelsize=10)
tax.set_yticks([0, 50, 100, 150, 200])

# ---------- biggest tests and whose land ----------
bt = tt + 790
fig.text(.045, fy(bt), "The biggest tests", fontproperties=DISP, fontsize=21, color=FG, va="top")
fig.text(.545, fy(bt), "Whose land, and islands", fontproperties=DISP, fontsize=21, color=FG, va="top")
bax = fig.add_axes([.205, fy(bt + 470), .3, fh(400)]); bax.set_facecolor(BGc)
B = R["biggest"][:9]
for i, b in enumerate(B):
    c = CCOL[CI[b["country"]]]
    bax.plot([0, b["mid"] / 1000], [i, i], color=c, lw=2.2)
    if b["hi"] > b["lo"]:
        bax.plot([b["lo"] / 1000, b["hi"] / 1000], [i, i], color=FG, lw=.9, ls=(0, (2, 2)))
    bax.scatter([b["mid"] / 1000], [i], s=46, color=c, edgecolors="white", zorder=3)
bax.set_yticks(range(len(B))); bax.set_yticklabels([f"{b['name'].replace(', Soviet test no. 130', '').replace('Soviet test no.', 'Soviet no.')}, {b['year']}" for b in B], fontsize=9.6)
bax.invert_yaxis(); spines(bax); bax.set_xlim(0, 52); bax.set_xticks([0, 10, 20, 30, 40, 50]); bax.set_xticklabels(["0", "10", "20", "30", "40", "50 Mt"], fontsize=9.5)
bax.grid(axis="x", color=RULE, lw=.8); bax.set_axisbelow(True)
fig.text(.205, fy(bt + 530), f"Tsar Bomba, about 50 megatons, was {R['tsar']['x_hiroshima']:,.0f} times the Hiroshima\nbomb. Dotted: range of the source's estimates.", fontsize=9.3, color=MUT, va="top", linespacing=1.35)
wax = fig.add_axes([.62, fy(bt + 430), .355, fh(330)]); wax.set_facecolor(BGc)
KC = ["#8D939B", "#C8442A", "#E8A33A", "#5FA8D3"]
rows = [("Tests", [k["n"] for k in R["kinds"]], KC), ("Yield", [k["yield_mid"] for k in R["kinds"]], KC),
        ("Tests", [R["island_n"], R["n"] - R["island_n"]], ["#2E86AB", "#CFC9BC"]), ("Yield", [R["island_yield"], R["yield_total_mid"] - R["island_yield"]], ["#2E86AB", "#CFC9BC"])]
for i, (nm, v, cs) in enumerate(rows):
    yv = i + (.55 if i >= 2 else 0); tot = sum(v); x = 0
    for j, a in enumerate(v):
        wax.barh(yv, a / tot * 100, left=x, color=cs[j], height=.74, lw=0)
        if a / tot > .07:
            wax.text(x + 1.5, yv, f"{100 * a / tot:.0f}%", va="center", color="white", fontsize=10, fontweight="medium")
        x += a / tot * 100
wax.set_yticks([0, 1, 2.55, 3.55]); wax.set_yticklabels(["Tests", "Yield", "Tests", "Yield"], fontsize=10)
wax.invert_yaxis(); wax.set_xlim(0, 100); wax.set_xticks([]); [wax.spines[s].set_visible(False) for s in wax.spines]
wax.tick_params(length=0)
wax.text(0, -.6, "Status of the land at the time of the test", fontsize=9.5, color=MUT)
wax.text(0, 1.95, "On islands or on the mainland", fontsize=9.5, color=MUT)
lg = [("Own national territory", KC[0]), ("Own colony, overseas or trust territory", KC[1]), ("Another state's territory or colony", KC[2]), ("Open ocean", KC[3]), ("On islands", "#2E86AB"), ("Mainland", "#CFC9BC")]
for k, (nm, c) in enumerate(lg):
    xx = .62 + (k // 4) * .25; yy = bt + 446 + (k % 4) * 30
    fig.add_artist(Rectangle((xx, fy(yy + 15)), .011, fh(14), transform=fig.transFigure, fc=c, ec="none"))
    fig.text(xx + .015, fy(yy), nm, fontsize=8.8, color=FG, va="top", linespacing=1.15)
fig.text(.62, fy(bt + 578), f"Every French and British test was outside the home\ncountry: in Algeria, French Polynesia, Australia,\nKiribati and Nevada.", fontsize=9.3, color=MUT, va="top", linespacing=1.35)

# ---------- footer ----------
ft = bt + 745
fig.add_artist(Rectangle((.045, fy(ft)), .91, fh(2), transform=fig.transFigure, fc=FG, ec="none"))
fig.text(.045, fy(ft + 16), "Sources: Bergkvist and Ferm (2000), Nuclear Explosions 1945 to 1998 (FOA and SIPRI), via data is plural and TidyTuesday;\n"
         "North Korea 2006 to 2017 and some test names: Wikipedia (CC BY-SA). Natural Earth. Yields are estimates: circles and totals use the\n"
         "middle of each range. Salvo tests count once. Land status at the time of the test. A map of explosions, not of exposure or harm.",
         fontsize=9.4, color=MUT, va="top", linespacing=1.45)
fig.text(.045, fy(ft + 200), "Analysis and chart: Tristan Hotham, with Python and matplotlib", fontsize=10, color=FG, va="top")
fig.text(.955, fy(ft + 200), "maps.tristanhotham.com/nuclear-tests", fontsize=10, color=FG, va="top", ha="right", fontweight="medium")
assert ft + 240 < Hpx, ft
out = os.path.join(ROOT, "reddit", "every_nuclear_test.png")
fig.savefig(out, dpi=200, facecolor=BGc)
from PIL import Image
print("FAIL", FAIL); im = Image.open(out); print("collage", im.size, "labels", len(boxes), "leaders", len(placed))

assert not FAIL, FAIL
