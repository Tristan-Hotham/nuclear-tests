"""Static figures for the paper (release/paper/f_*.png), the blog (release/blog/b_*.png) and the social card (header.png).
All numbers from data/results.json and data/tests.csv."""
import shutil
from figstyle import *
from matplotlib.patches import Rectangle

R = jload(f"{DATA}/results.json")
D = tests(); T = D[D.is_test == 1].copy()
PAP = os.path.join(ROOT, "release", "paper"); BLOG = os.path.join(ROOT, "release", "blog")
for d in (PAP, BLOG):
    os.makedirs(d, exist_ok=True)
CI = {c[0]: i for i, c in enumerate(COUNTRIES)}
T["ci"] = T.country.map(CI)
SEAc = "#E9EEF1"; LANDc = "#DEDAD0"


def both(fig, name, dpi=200):
    p = f"{PAP}/f_{name}.png"; save(fig, p, dpi)
    shutil.copy(p, f"{BLOG}/b_{name}.png")


def treaties(ax, top, small=False, fs=10):
    ax.axvspan(1958.84, 1961.67, color="#E6E1D6", zorder=0, lw=0)
    ax.text(1960.25, top * .995, "testing\npause", ha="center", va="top", fontsize=fs - 1, color=MUT, linespacing=1.0)
    for x, t, row in ((1963.6, "Partial Test Ban Treaty, 1963", 0), (1974.5, "Threshold Test Ban Treaty, 1974", 1), (1996.73, "Comprehensive Test-Ban Treaty, 1996", 0)):
        ax.axvline(x, color=FG, lw=1, ls=(0, (3, 3)), alpha=.7, zorder=3)
        ax.text(x + .6, top * (.98 - .07 * row), t, fontsize=fs, color=FG, va="top", zorder=4,
                path_effects=[__import__("matplotlib.patheffects", fromlist=["x"]).withStroke(linewidth=3, foreground=BG)])


def years_fig(ax, mode="country", fs=10):
    Y = np.array(R["years"] if mode == "country" else R["years_env"])
    cols = CCOL if mode == "country" else ECOL
    bottom = np.zeros(len(Y))
    for j in range(1, Y.shape[1]):
        ax.bar(Y[:, 0], Y[:, j], bottom=bottom, color=cols[j - 1], width=.86, lw=0, zorder=2)
        bottom += Y[:, j]
    top = 200
    ax.set_ylim(0, top); ax.set_xlim(1944.2, 2017.8)
    treaties(ax, top, fs=fs)
    spines(ax); ax.grid(axis="y", color=RULE, lw=.8, zorder=0); ax.set_axisbelow(True)
    ax.tick_params(labelsize=fs)
    return ax


# ---------- years by country ----------
fig, ax = plt.subplots(figsize=(12, 5.4), facecolor=BG); ax.set_facecolor(BG)
years_fig(ax)
ax.text(1961.6, R["peak_n"] - 4, f"{R['peak_n']} tests in {R['peak_year']}", ha="right", va="top", fontsize=11, fontweight="medium")
ax.set_ylabel("tests per year", fontsize=11)
h = [Rectangle((0, 0), 1, 1, fc=c[1]) for c in COUNTRIES]
ax.legend(h, [c[0] for c in COUNTRIES], ncol=2, loc="center right", bbox_to_anchor=(1, .5), frameon=False, fontsize=10)
fig.tight_layout(); both(fig, "years")

# ---------- years by environment ----------
fig, ax = plt.subplots(figsize=(12, 5.0), facecolor=BG); ax.set_facecolor(BG)
years_fig(ax, "env")
ax.set_ylabel("tests per year", fontsize=11)
ax.text(1947, 120, f"Before the 1963 treaty:\n{R['pre_atm_pct']:.0f}% in the atmosphere\nor underwater", fontsize=11, color=ENVS[0][1], va="top")
ax.text(1978, 120, f"After it:\n{R['post_ug_pct']:.0f}% underground", fontsize=11, color=ENVS[2][1], va="top")
h = [Rectangle((0, 0), 1, 1, fc=e[1]) for e in ENVS]
ax.legend(h, [e[0] for e in ENVS], ncol=3, loc="upper right", bbox_to_anchor=(1, .78), frameon=False, fontsize=10)
fig.tight_layout(); both(fig, "env")

# ---------- world map ----------
EXT = ext_of(-180, -50, 180, 84)
ASP = (EXT[3] - EXT[2]) / (EXT[1] - EXT[0])


def world_map(ax, sc=1.0, label_sites=True, fs=10):
    world(ax, EXT, land=LANDc, sea=SEAc, ec="#FFFFFF", lw=.35)
    o = T.sort_values("yield_kt_mid", ascending=False)
    x, y = proj(o.lon.values, o.lat.values)
    r = .78 * sc * np.cbrt(o.yield_kt_mid.fillna(1).clip(lower=.05).values)
    r = np.maximum(r, 1.4 * sc)
    big = r > 9 * sc
    ax.scatter(x[big], y[big], s=r[big] ** 2, c=[CCOL[i] for i in o.ci[big]], alpha=.28, lw=1.1 * sc, edgecolors=[CCOL[i] for i in o.ci[big]], zorder=5)
    ax.scatter(x[~big], y[~big], s=r[~big] ** 2, c=[CCOL[i] for i in o.ci[~big]], alpha=.75, lw=.3 * sc, edgecolors="white", zorder=6)
    W = D[D.is_test == 0]; wx, wy = proj(W.lon.values, W.lat.values)
    ax.scatter(wx, wy, s=(.78 * sc * np.cbrt(W.yield_kt_mid.values)) ** 2, facecolors="none", edgecolors=FG, lw=1.4 * sc, zorder=7)
    return ax


fig, ax = plt.subplots(figsize=(12, 12 * ASP), facecolor=BG)
world_map(ax)
fig.subplots_adjust(0, 0, 1, 1); both(fig, "map")

# ---------- yield by site ----------
S = [R["site"][k] for k in R["site_rank_yield"][:14]]
fig, ax = plt.subplots(figsize=(11, 6.4), facecolor=BG); ax.set_facecolor(BG)
for i, s in enumerate(S):
    c = CCOL[CI[s["countries"][0]]]
    ax.barh(i, s["yield_mid"] / 1000, color=c, height=.62, zorder=2)
    ax.plot([s["yield_lo"] / 1000, s["yield_hi"] / 1000], [i, i], color=FG, lw=1.1, zorder=3)
    ax.text(max(s["yield_hi"], s["yield_mid"]) / 1000 + 4, i, f"{s['yield_mid'] / 1000:,.1f} Mt  ({s['n']:,} tests)", va="center", fontsize=10)
ax.set_yticks(range(len(S))); ax.set_yticklabels([s["name"].replace(" and nearby ranges", "").replace(" (mostly peaceful explosions)", "") for s in S], fontsize=10)
ax.invert_yaxis(); spines(ax); ax.set_xlabel("total yield, megatons (central estimate; line: range of estimates)", fontsize=10)
ax.set_xlim(0, 420); ax.grid(axis="x", color=RULE, lw=.8, zorder=0)
fig.tight_layout(); both(fig, "yield")

# ---------- biggest tests ----------
B = R["biggest"]
fig, ax = plt.subplots(figsize=(11, 6.8), facecolor=BG); ax.set_facecolor(BG)
for i, b in enumerate(B):
    c = CCOL[CI[b["country"]]]
    ax.plot([0, b["mid"] / 1000], [i, i], color=c, lw=2, zorder=2)
    if b["hi"] > b["lo"]:
        ax.plot([b["lo"] / 1000, b["hi"] / 1000], [i, i], color=FG, lw=1, ls=(0, (2, 2)), zorder=2)
    ax.scatter([b["mid"] / 1000], [i], s=60, color=c, edgecolors="white", zorder=3)
    t = f"{b['site'].replace(' (Christmas Island)', '')}, {b['year']}"
    if b["hi"] / 1000 < 36:
        ax.text(b["hi"] / 1000 + .8, i, t, va="center", fontsize=9.5, color=MUT)
    else:
        ax.text(b["mid"] / 1000 - 1, i - .12, t, va="bottom", ha="right", fontsize=9.5, color=MUT)
ax.set_yticks(range(len(B))); ax.set_yticklabels([b["name"].replace(", Soviet test no. 130", "") for b in B], fontsize=10)
ax.invert_yaxis(); spines(ax); ax.set_xlim(0, 52); ax.set_xlabel("yield, megatons (central estimate; dotted: range of estimates)", fontsize=10)
ax.grid(axis="x", color=RULE, lw=.8, zorder=0)
h = [Rectangle((0, 0), 1, 1, fc=COUNTRIES[i][1]) for i in (0, 1)]
ax.legend(h, [COUNTRIES[0][0], COUNTRIES[1][0]], loc="lower right", frameon=False, fontsize=10)
fig.tight_layout(); both(fig, "biggest")

# ---------- whose land ----------
KC = ["#8D939B", "#C8442A", "#E8A33A", "#5FA8D3"]
fig, ax = plt.subplots(figsize=(11, 3.9), facecolor=BG); ax.set_facecolor(BG)
rows = [("Tests", [k["n"] for k in R["kinds"]], KC), ("Yield", [k["yield_mid"] for k in R["kinds"]], KC),
        ("Tests", [R["island_n"], R["n"] - R["island_n"]], ["#2E86AB", "#CFC9BC"]), ("Yield", [R["island_yield"], R["yield_total_mid"] - R["island_yield"]], ["#2E86AB", "#CFC9BC"])]
for i, (nm, v, cs) in enumerate(rows):
    y = i + (.5 if i >= 2 else 0); tot = sum(v); x = 0
    for j, a in enumerate(v):
        ax.barh(y, a / tot * 100, left=x, color=cs[j], height=.72, lw=0)
        if a / tot > .045:
            ax.text(x + 1, y, f"{100 * a / tot:.0f}%", va="center", color="white", fontsize=10, fontweight="medium")
        x += a / tot * 100
ax.set_yticks([0, 1, 2.5, 3.5]); ax.set_yticklabels(["Tests", "Yield", "Tests", "Yield"], fontsize=10.5)
ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xticks([]); [ax.spines[s].set_visible(False) for s in ax.spines]
ax.text(0, -.62, "Status of the land at the time", fontsize=10, color=MUT); ax.text(0, 1.88, "Islands or mainland", fontsize=10, color=MUT)
h = [Rectangle((0, 0), 1, 1, fc=c) for c in KC + ["#2E86AB", "#CFC9BC"]]
ax.legend(h, KINDS[:4] + ["On islands", "Mainland"], ncol=3, loc="upper center", bbox_to_anchor=(.5, -.02), frameon=False, fontsize=9.5)
fig.tight_layout(); both(fig, "land")

# ---------- North Korea ----------
N = R["nk"]["tests"]
fig, ax = plt.subplots(figsize=(10, 3.4), facecolor=BG); ax.set_facecolor(BG)
for i, t in enumerate(N):
    ax.barh(i, t["hi"] - t["lo"], left=t["lo"], color=COUNTRIES[7][1], alpha=.55, height=.5)
    ax.scatter([(t["lo"] + t["hi"]) / 2], [i], color=COUNTRIES[7][1], s=30, zorder=3)
    ax.text(t["hi"] + 3, i, f"{t['lo']:g} to {t['hi']:g} kt", va="center", fontsize=10)
ax.axvline(R["hiroshima_kt"], color=HOT, ls=(0, (4, 3)), lw=1)
ax.text(R["hiroshima_kt"] + 2, 5.45, "Hiroshima bomb", color=HOT, fontsize=9.5)
ax.set_yticks(range(6)); ax.set_yticklabels([t["date"] for t in N], fontsize=10); ax.invert_yaxis()
ax.set_xlim(0, 330); spines(ax); ax.set_xlabel("estimated yield, kilotons (range as given on Wikipedia)", fontsize=10)
fig.tight_layout(); save(fig, f"{PAP}/f_nk.png")

# ---------- header 1200 x 630 ----------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
fig.text(.045, .87, "Every nuclear", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .72, "test", fontproperties=DISP, fontsize=50, color=HOT, va="top")
fig.text(.045, .55, f"{R['n']:,} tests by eight countries,\n1945 to 2017. {R['peak_n']} in {R['peak_year']} alone;\n"
         f"{R['island_yield_pct']:.0f}% of all the explosive yield\nwas set off on islands.", fontproperties=SERP, fontsize=17, color=FG, va="top", linespacing=1.5)
fig.text(.045, .07, "maps.tristanhotham.com/nuclear-tests", fontsize=11, color=MUT)
ax = fig.add_axes([.40, .14, .59, .59 * 12 / 6.3 * ASP]); world_map(ax, sc=.7)
save(fig, os.path.join(ROOT, "header.png"), dpi=100)
from PIL import Image
assert Image.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
print("figures:", sorted(os.listdir(PAP)), sorted(os.listdir(BLOG)))
