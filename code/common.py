"""Shared paths, groupings and helpers for the nuclear-tests project.

Raw inputs (read in place, never modified):
  /home/claude/newdata/raw8/nuclear/nuclear_explosions.csv
      SIPRI list of 2,051 nuclear explosions, 16 July 1945 to 30 May 1998, from the report by Bergkvist and Ferm (2000),
      Nuclear Explosions 1945 to 1998 (Swedish Defence Research Establishment, FOA, and Stockholm International Peace Research
      Institute, SIPRI), as published by data is plural (github.com/data-is-plural/nuclear-explosions) and
      rfordatascience/tidytuesday (2019-08-20), credit Jesus Castagnetto. Date, testing state, site code, position, body and
      surface wave magnitudes, depth, lower and upper yield estimates (kilotons), purpose, name and method of deployment.
  /home/claude/newdata/raw8/nuclear/wiki_*.json
      Parsed English Wikipedia pages (CC BY-SA 4.0), fetched 2026: List of nuclear weapons tests (revision 1378389080),
      List of nuclear weapons tests of North Korea (1378498359), Pokhran-II (1376678335), Chagai-I (1370612927).
      Used for the six North Korean tests of 2006 to 2017 (dates, positions and yield ranges from the page text only), for
      the names of the largest Soviet tests, and for test names in India and Pakistan.
  /home/claude/newdata/raw/geo/  Natural Earth countries, land and populated places (public domain).
"""
import json, gzip, os, re
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("NUC_RAW", "/home/claude/newdata/raw8/nuclear")
GEO = os.environ.get("NUC_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("NUC_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("NUCTMP", "/dev/shm/nuclear"), "work")
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "nuclear-tests"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
WIKI_REV = {"List of nuclear weapons tests": 1378389080, "List of nuclear weapons tests of North Korea": 1378498359,
            "Pokhran-II": 1376678335, "Chagai-I": 1370612927}

# testing states (order = legend order)
COUNTRIES = [("United States", "#2C6FBB"), ("Soviet Union", "#C23B22"), ("France", "#16998A"), ("United Kingdom", "#7B5EA7"),
             ("China", "#E0A01B"), ("India", "#EE7D2B"), ("Pakistan", "#3E8E41"), ("North Korea", "#C2408C")]
CSHORT = ["US", "USSR", "France", "UK", "China", "India", "Pakistan", "N. Korea"]
C_OF = {"USA": 0, "USSR": 1, "FRANCE": 2, "UK": 3, "CHINA": 4, "INDIA": 5, "PAKIST": 6, "NKOREA": 7}

# where the device went off (the Partial Test Ban Treaty of 1963 banned the first two)
ENVS = [("In the atmosphere or space", "#E4572E"), ("Underwater", "#2E86AB"), ("Underground", "#5B5F66")]
ENV_OF = {"ATMOSPH": 0, "AIRDROP": 0, "TOWER": 0, "BALLOON": 0, "SURFACE": 0, "BARGE": 0, "ROCKET": 0, "SPACE": 0, "SHIP": 0,
          "WATERSUR": 0, "WATER SU": 0, "UW": 1,
          "SHAFT": 2, "TUNNEL": 2, "SHAFT/GR": 2, "SHAFT/LG": 2, "UG": 2, "GALLERY": 2, "MINE": 2, "CRATER": 2}
TYPE_NAME = {"ATMOSPH": "in the atmosphere", "AIRDROP": "air drop", "TOWER": "on a tower", "BALLOON": "from a balloon",
             "SURFACE": "on the surface", "BARGE": "on a barge", "ROCKET": "on a rocket", "SPACE": "in space (rocket)",
             "SHIP": "on a ship", "WATERSUR": "on the water surface", "WATER SU": "on the water surface", "UW": "underwater",
             "SHAFT": "underground, vertical shaft", "TUNNEL": "underground, tunnel", "SHAFT/GR": "underground, shaft (salvo)",
             "SHAFT/LG": "underground, shaft (salvo)", "UG": "underground", "GALLERY": "underground, gallery",
             "MINE": "underground, in a mine", "CRATER": "shallow buried (cratering)"}
PURPOSE_NAME = {"WR": "weapons development", "WE": "weapons effects", "PNE": "peaceful nuclear explosion", "SE": "safety experiment",
                "FMS": "study of nuclear explosion phenomena", "SAM": "accident or emergency mode study", "COMBAT": "wartime use",
                "TRANSP": "transport and storage safety", "ME": "military exercise", "SB": "fundamental science", "PNE:PLO": "peaceful (Plowshare)",
                "PNE:V": "peaceful (Vela Uniform seismic research)"}

# sites: (key, name, place today, kind of land at the time, island?, map label position [lat, lon])
# kind: 0 = the testing state's own territory; 1 = a colony, overseas or trust territory of the testing state;
#       2 = another state's territory; 3 = open ocean or space; 4 = wartime use (not a test)
KINDS = ["Own national territory", "Own colony, overseas or trust territory", "Another state's territory or colony", "Open ocean or space", "Wartime use"]
# the same site can be a different kind of land for a guest: British tests in Nevada, US tests at British-held Kiritimati
KIND_GUEST = {("United Kingdom", "nevada"): 2, ("United States", "kiritimati"): 2}
SITES = [
    ("nevada", "Nevada Test Site and nearby ranges", "Nevada, United States", 0, False),
    ("trinity", "Trinity, Alamogordo", "New Mexico, United States", 0, False),
    ("usmain", "Other US mainland sites", "New Mexico, Colorado and Mississippi, United States", 0, False),
    ("amchitka", "Amchitka Island", "Aleutian Islands, Alaska, United States", 0, True),
    ("bikini", "Bikini Atoll", "Marshall Islands", 1, True),
    ("enewetak", "Enewetak Atoll", "Marshall Islands", 1, True),
    ("johnston", "Johnston Atoll", "Central Pacific (US territory)", 1, True),
    ("kiritimati", "Kiritimati (Christmas Island)", "Kiribati", 1, True),
    ("malden", "Malden Island", "Kiribati", 1, True),
    ("ocean", "Open ocean (Pacific and South Atlantic)", "High seas", 3, False),
    ("semipalatinsk", "Semipalatinsk Test Site", "Kazakhstan", 0, False),
    ("novaya", "Novaya Zemlya", "Arctic Russia", 0, True),
    ("kapustin", "Kapustin Yar", "Astrakhan region, Russia", 0, False),
    ("azgir", "Azgir", "Kazakhstan", 0, False),
    ("ussrpne", "Other Soviet sites (mostly peaceful explosions)", "Russia, Kazakhstan, Ukraine, Uzbekistan and Turkmenistan", 0, False),
    ("lopnur", "Lop Nur", "Xinjiang, China", 0, False),
    ("reggane", "Reggane", "Algeria", 1, False),
    ("inekker", "In Ekker", "Algeria", 1, False),
    ("moruroa", "Moruroa Atoll", "French Polynesia", 1, True),
    ("fangataufa", "Fangataufa Atoll", "French Polynesia", 1, True),
    ("montebello", "Montebello Islands", "Western Australia", 2, True),
    ("emu", "Emu Field", "South Australia", 2, False),
    ("maralinga", "Maralinga", "South Australia", 2, False),
    ("pokhran", "Pokhran", "Rajasthan, India", 0, False),
    ("chagai", "Ras Koh Hills, Chagai", "Balochistan, Pakistan", 0, False),
    ("kharan", "Kharan Desert", "Balochistan, Pakistan", 0, False),
    ("punggye", "Punggye-ri", "North Hamgyong, North Korea", 0, False),
    ("hiroshima", "Hiroshima", "Japan", 4, False),
    ("nagasaki", "Nagasaki", "Japan", 4, False),
]
SKEY = [s[0] for s in SITES]
SI = {k: i for i, k in enumerate(SKEY)}

# SIPRI site codes (including the typing errors in the source) to sites
REGION_SITE = {
    "NTS": "nevada", "NELLIS NV": "nevada", "MELLIS NV": "nevada", "C. NEVADA": "nevada", "FALLON NV": "nevada",
    "ALAMOGORDO": "trinity", "CARLSBAD NM": "usmain", "FARMINGT NM": "usmain", "GRAND V CO": "usmain", "RIFLE CO": "usmain",
    "HATTIESB MS": "usmain", "HATTIESE MS": "usmain", "AMCHITKA AK": "amchitka", "BIKINI": "bikini", "ENEWETAK": "enewetak",
    "JOHNSTON IS": "johnston", "CHRISTMAS IS": "kiritimati", "MALDEN IS": "malden", "PACIFIC": "ocean", "OFFUSWCOAST": "ocean",
    "S.ATLANTIC": "ocean", "S. ATLANTIC": "ocean", "HIROSHIMA": "hiroshima", "NAGASAKI": "nagasaki",
    "SEMI KAZAKH": "semipalatinsk", "NZ RUSS": "novaya", "KZ RUSS": "novaya", "N2 RUSS": "novaya",
    "MTR RUSS": "kapustin", "HTR RUSS": "kapustin", "AZGIR": "azgir", "AZGIR KAZAKH": "azgir", "AZGIE KAZAKH": "azgir",
    "LOP NOR": "lopnur", "REGGANE ALG": "reggane", "IN ECKER ALG": "inekker",
    "MURUROA": "moruroa", "MUEUEOA": "moruroa", "MURUEOA": "moruroa", "MURUHOA": "moruroa", "HURUROA": "moruroa",
    "W MURUROA": "moruroa", "WSW MURUROA": "moruroa", "FANGATAUFA": "fangataufa", "FANGATAUFAA": "fangataufa",
    "MONTEB AUSTR": "montebello", "EMU AUSTR": "emu", "MARALI AUSTR": "maralinga",
    "POKHRAN": "pokhran", "CHAGAI": "chagai", "KHARAN": "kharan"}
# every other SIPRI code is a Soviet site outside the main ranges -> "ussrpne"

# 24 records have no position (0, 0) in the source. They are placed at the median position of the other records with the
# same site code, or, for codes with no other record, of the code they repeat (BASHKI = BASHKIR, TUYMEN = TYUMEN), or at
# the place the code names (Pamuk gas field, Uzbekistan; the two Ukrainian peaceful explosions, Fakel in the Kharkiv region
# and Klivazh in the Donetsk region), and flagged as approximate.
POS_ALIAS = {"BASHKI RUSS": "BASHKIR RUSS", "TUYMEN RUSS": "TYUMEN RUSS", "PAMUK UZBEK": "UZBEK"}
FIX_POS = {"UKRAINE": (49.4, 35.4, "the Kharkiv region, Ukraine"), "UKEAINE": (48.2, 38.2, "the Donetsk region, Ukraine")}

# map focus groups (page buttons and collage labels)
GROUPS = [("Nevada", ["nevada"]), ("Semipalatinsk", ["semipalatinsk"]), ("Novaya Zemlya", ["novaya"]), ("Lop Nur", ["lopnur"]),
          ("Moruroa and Fangataufa", ["moruroa", "fangataufa"]), ("Bikini and Enewetak", ["bikini", "enewetak"]),
          ("Kiritimati, Malden and Johnston", ["kiritimati", "malden", "johnston"]), ("Australia", ["montebello", "emu", "maralinga"]),
          ("Algeria", ["reggane", "inekker"]), ("Punggye-ri", ["punggye"]), ("India and Pakistan", ["pokhran", "chagai", "kharan"])]

# treaties and pauses (for charts); dates from the treaty texts
TREATIES = [(1958.84, 1961.67, "US, Soviet and British testing pause, November 1958 to September 1961"),
            (1963.6, None, "Partial Test Ban Treaty, signed 5 August 1963: no tests in the atmosphere, in space or underwater"),
            (1974.5, None, "Threshold Test Ban Treaty, signed July 1974: US and Soviet tests limited to 150 kilotons"),
            (1996.73, None, "Comprehensive Nuclear-Test-Ban Treaty opened for signature, 24 September 1996")]
PTBT_DATE = 19630805
ALGERIA_INDEP = 19620705
CTBT_DATE = 19960924


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


class NpEnc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.bool_): return bool(o)
        if isinstance(o, np.ndarray): return o.tolist()
        return super().default(o)


def jsave(obj, path, indent=None):
    obj = json.loads(json.dumps(obj, cls=NpEnc, allow_nan=False))
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "mt": return f"{float(v) / 1000:,.1f}"           # kilotons -> megatons, one decimal
    if f == "mt0": return f"{round(float(v) / 1000):,}"       # kilotons -> megatons, whole
    if f == "x": return f"{round(float(v)):,}"
    raise ValueError(f)


KEEP = ("DOI", "DOI_URL", "BLOG_URL")


def fill(text, R, fmtf=fmt):
    """Replace {{path|format}} tokens with numbers from results.json; keep the publisher's placeholders and IMG tokens."""
    def rep(m):
        key = m.group(1)
        if key in KEEP or key.startswith("IMG"):
            return m.group(0)
        return fmtf(get(R, key), m.group(3))
    out = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", rep, text)
    left = [x for x in re.findall(r"\{\{([^}|]+)", out) if x not in KEEP and not x.startswith("IMG")]
    assert not left, left[:5]
    return out


def ymd(d):
    d = str(int(d))
    return f"{d[:4]}-{d[4:6]}-{d[6:]}"


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def longdate(d):
    d = str(int(d))
    return f"{int(d[6:])} {MONTHS[int(d[4:6]) - 1]} {d[:4]}"
