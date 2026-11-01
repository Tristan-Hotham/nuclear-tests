"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/<NAME>.pdf and .tex (figures f_*.png beside them). The DOI stays a placeholder (10.5281/zenodo.23857489)."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
NOTES = jload(f"{DATA}/site_notes.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Every_Nuclear_Test"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f in (None, "raw"): return tex(str(v))
    return tex(fmt(v, f))


mt = lambda v: f"{v / 1000:,.1f}" if v >= 100 else f"{v / 1000:,.3f}"
WT = R["wiki_totals"]; WN = {"US": "US", "USSR": "USSR", "France": "France", "UK": "UK", "China": "China", "India": "India", "Pakistan": "Pakistan", "N. Korea": "North Korea"}
rows = "".join(f"{tex(c['name'])} & {c['n']:,} & {WT[WN[c['short']]]['tests']:,} & {c['first_year']} & {c['last_year']} & {c['atm'] + c['uw']:,} & {c['ug']:,} & {mt(c['yield_mid'])} & {mt(c['yield_lo'])} to {mt(c['yield_hi'])}\\\\\n" for c in R["countries"])
TC = ("\\begin{table}[tbp]\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}\\caption{Tests by country: count in this study and in the Wikipedia list, first and last year, atmospheric or underwater and underground tests, and total yield in megatons (central estimate and range).}\\label{tab:countries}"
      "\\begin{tabular}{lrrrrrrrr}\\toprule Country & Tests & Wikipedia & First & Last & Air/water & Underground & Yield Mt & Range Mt\\\\\\midrule\n" + rows +
      f"\\midrule Total & {R['n']:,} & {R['wiki_tests']:,} & 1945 & 2017 & {R['atm_total']:,} & {R['env'][2]['n']:,} & {mt(R['yield_total_mid'])} & {mt(R['yield_total_lo'])} to {mt(R['yield_total_hi'])}\\\\" + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for s in sorted([s for s in R["sites"] if s["kind"] != 4], key=lambda s: -s["n"]):
    yrs = str(s["y0"]) if s["y0"] == s["y1"] else f"{s['y0']} to {s['y1']}"
    rows += (f"\\textbf{{{tex(s['name'])}}}, {tex(s['today'])} & {s['n']:,} & {yrs} & {mt(s['yield_mid'])} & {tex(KINDS[s['kind']])} & {tex(NOTES[s['key']])}\\\\\n")
TS = ("{\\footnotesize\\begin{longtable}{p{3.3cm}rp{1.2cm}rp{2.2cm}p{5.6cm}}\\caption{Test sites: tests, years, total yield (megatons, central estimate), status of the land at the time (for the testing state that used it most) and notes. Sources in brackets; see the reference list.}\\label{tab:sites}\\\\"
      "\\toprule Site & Tests & Years & Yield & Land & Note\\\\\\midrule\\endfirsthead\\toprule Site & Tests & Years & Yield & Land & Note\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3)), t)
t = t.replace("{{TABLE_COUNTRIES}}", TC).replace("{{TABLE_SITES}}", TS)
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:3]
t = t.replace("@@DOI@@", "https://doi.org/\\{\\{DOI\\}\\}")
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
for bad in ("DSIT", "DCMS"):
    assert bad not in txt
