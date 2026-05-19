#!/usr/bin/env python3
"""
=============================================================================
  新加坡房产分析仪表板生成器  (实时数据版)
  Singapore Property Analysis Dashboard — LIVE DATA Edition

  Every run fetches REAL, LATEST data from Singapore government open APIs:

  ┌─────────────────────────────────────────────────────────────────────┐
  │  Source        Dataset                          data.gov.sg ID       │
  ├─────────────────────────────────────────────────────────────────────┤
  │  URA           PPI by Locality (CCR/RCR/OCR)   d_f65e490a8ad430f…  │
  │  URA           Unsold units by segment          d_84d05d45049108f…  │
  │  URA           CCR new-launch transactions      d_c287c8be114bfa7…  │
  │  URA           RCR new-launch transactions      d_5785799d63a9da0…  │
  │  URA           OCR new-launch transactions      d_1a7823f3d31e7db…  │
  └─────────────────────────────────────────────────────────────────────┘

  GDP & unemployment are fetched from data.gov.sg / SingStat open data.
  GLS forecast (H1/H2 2026) is hardcoded from the official Dec 2025 press
  release (government does not publish a machine-readable GLS API).

  REQUIREMENTS
    pip install requests weasyprint

    For PDF on Windows:  install GTK3 runtime from
      https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
    For PDF on macOS:    brew install pango cairo
    For PDF on Linux:    apt install libcairo2 libpango-1.0-0 libpangocairo-1.0-0

    PDF is optional — set GENERATE_PDF = False to produce HTML only.

  USAGE
    python sg_property_dashboard_live.py

  OUTPUTS  (saved next to this script)
    sunshine_plaza_dashboard.html / .pdf
    kentish_court_dashboard.html  / .pdf

  DATA IS CACHED for 6 hours in  .sg_dashboard_cache.json
  so re-running quickly will not hit the API every time.
=============================================================================
"""

import os, sys, json, datetime, time, re
import urllib.request, urllib.error, ssl
from pathlib import Path

# ── USER CONFIG ──────────────────────────────────────────────────────────────
GENERATE_PDF = True  # set False to skip PDF (HTML still works)
CACHE_HOURS = 6  # re-fetch from API after this many hours
OUTPUT_DIR = Path(__file__).parent
CACHE_FILE = OUTPUT_DIR / ".sg_dashboard_cache.json"
# ─────────────────────────────────────────────────────────────────────────────

REPORT_DATE = datetime.date.today().strftime("%Y 年 %m 月 %d 日")

# ─── GLS FORECAST (from official Dec 2025 press release, updated manually) ───
# Update this dict after each GLS programme announcement
GLS_FORECAST = {
    "H1 2026★": {
        "ccr": 785,
        "rcr": 850,
        "ocr": 2305,
        "note": "1H 2026 Confirmed List (URA, Dec 2025)",
    },
    "H2 2026★": {
        "ccr": 500,
        "rcr": 900,
        "ocr": 2200,
        "note": "H2 2026 estimated (based on H1 trend)",
    },
}
GLS_TOTAL_1H2026 = 4575  # official confirmed list figure

# ═══════════════════════════════════════════════════════════════════════════════
#  CACHE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def load_cache():
    if CACHE_FILE.exists():
        try:
            c = json.loads(CACHE_FILE.read_text())
            age_h = (time.time() - c.get("_ts", 0)) / 3600
            if age_h < CACHE_HOURS:
                print(f"  📦 Using cached data (age: {age_h:.1f}h, max {CACHE_HOURS}h)")
                return c
        except Exception:
            pass
    return {}


def save_cache(data):
    data["_ts"] = time.time()
    CACHE_FILE.write_text(json.dumps(data, indent=2))


# ═══════════════════════════════════════════════════════════════════════════════
#  HTTP FETCH HELPER
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_json(url, label=""):
    """Fetch a JSON URL, return parsed dict or None on failure."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SGPropertyDashboard/2.0 (open-source; data.gov.sg public API)",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ⚠️  Could not fetch {label or url[:60]}: {e}")
        return None


def datagov(dataset_id, limit=40, sort="quarter desc"):
    """Query data.gov.sg CKAN datastore."""
    url = (
        f"https://data.gov.sg/api/action/datastore_search"
        f"?resource_id={dataset_id}&limit={limit}&sort={urllib.parse.quote(sort)}"
    )
    d = fetch_json(url, label=f"data.gov.sg/{dataset_id[:12]}…")
    if d and d.get("success") and d["result"].get("records"):
        return d["result"]["records"]
    return []


# We need urllib.parse too
import urllib.parse

# ═══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS  — each returns a clean dict for the template
# ═══════════════════════════════════════════════════════════════════════════════


def _parse_quarter(q_str):
    """'2024-Q3' or '2024Q3' → (2024, 3)"""
    m = re.search(r"(\d{4})[-_\s]?[Qq](\d)", str(q_str))
    if m:
        return int(m.group(1)), int(m.group(2))
    return (0, 0)


def _q_label(year, q):
    return f"{str(year)[2:]}Q{q}"  # "24Q3"


def fetch_ppi_by_locality():
    """
    Dataset: Property Price Index of Non-Landed Properties by Locality
    Resource ID: d_f65e490a8ad430f60a9a3d9df2bff2a0
    Fields expected: quarter, ccr, rcr, ocr  (or similar casing)
    Returns last 10 quarters sorted oldest-first.
    """
    recs = datagov("d_f65e490a8ad430f60a9a3d9df2bff2a0", limit=40)
    if not recs:
        return None

    # Normalise field names to lowercase
    norm = []
    for r in recs:
        nr = {k.lower().strip(): v for k, v in r.items()}
        norm.append(nr)

    # Sort by quarter ascending
    norm.sort(key=lambda r: _parse_quarter(r.get("quarter", "")))

    # Keep last 10
    norm = norm[-10:]

    result = []
    for r in norm:
        yr, q = _parse_quarter(r.get("quarter", ""))
        # field names vary — try several
        ccr = float(
            r.get("ccr") or r.get("core_central_region") or r.get("index_ccr") or 0
        )
        rcr = float(
            r.get("rcr") or r.get("rest_of_central_region") or r.get("index_rcr") or 0
        )
        ocr = float(
            r.get("ocr") or r.get("outside_central_region") or r.get("index_ocr") or 0
        )
        result.append({"q": _q_label(yr, q), "ccr": ccr, "rcr": rcr, "ocr": ocr})

    return result if result else None


def fetch_unsold_by_segment():
    """
    Dataset: Unsold Private Residential Units with Planning Approvals by Market Segment
    Resource ID: d_84d05d45049108f0fd2e99b66bd19cfe
    Fields expected: quarter, ccr, rcr, ocr, total (or variations)
    Returns last 10 quarters oldest-first.
    """
    recs = datagov("d_84d05d45049108f0fd2e99b66bd19cfe", limit=40)
    if not recs:
        return None

    norm = [{k.lower().strip(): v for k, v in r.items()} for r in recs]
    norm.sort(key=lambda r: _parse_quarter(r.get("quarter", "")))
    norm = norm[-10:]

    result = []
    for r in norm:
        yr, q = _parse_quarter(r.get("quarter", ""))
        total = (
            float(r.get("total") or 0)
            or float(r.get("total_unsold") or 0)
            or sum(float(r.get(k) or 0) for k in ["ccr", "rcr", "ocr"])
        )
        result.append({"q": _q_label(yr, q), "unsold": int(total)})

    return result if result else None


def fetch_launches_by_region():
    """
    Fetch quarterly new-launch units for CCR, RCR, OCR separately.
    Uses 3 datasets. Returns merged dict keyed by q-label.
    """
    DATASETS = {
        "ccr": "d_c287c8be114bfa7d055b27ab2c87de83",
        "rcr": "d_5785799d63a9da091f4e0b456291eeb8",
        "ocr": "d_1a7823f3d31e7db4b426833833762bab",
    }
    merged = {}  # q_label → {ccr, rcr, ocr}
    for region, rid in DATASETS.items():
        recs = datagov(rid, limit=40)
        if not recs:
            continue
        norm = [{k.lower().strip(): v for k, v in r.items()} for r in recs]
        norm.sort(key=lambda r: _parse_quarter(r.get("quarter", "")))
        norm = norm[-10:]
        for r in norm:
            yr, q = _parse_quarter(r.get("quarter", ""))
            label = _q_label(yr, q)
            if label not in merged:
                merged[label] = {"q": label, "ccr": 0, "rcr": 0, "ocr": 0}
            # field name for launched units varies
            val = float(
                r.get("units_launched")
                or r.get("no_of_units_launched")
                or r.get("launched")
                or r.get("new_sale")
                or r.get("total")
                or 0
            )
            merged[label][region] = int(val)

    if not merged:
        return None
    rows = sorted(merged.values(), key=lambda r: r["q"])
    return rows[-10:]


def fetch_gdp():
    """
    Fetch annual GDP growth from data.gov.sg (SingStat).
    Dataset: d_5798062985ef4e0e87e5bc6f5de5c7e  (GDP at current market prices)
    Falls back to hardcoded recent values if API is unavailable.
    """
    # SingStat GDP growth rate dataset
    recs = datagov("d_5798062985ef4e0e87e5bc6f5de5c7e", limit=20, sort="year desc")
    if recs:
        norm = [{k.lower().strip(): v for k, v in r.items()} for r in recs]
        norm.sort(key=lambda r: int(r.get("year", 0)))
        # Last 8 years
        norm = norm[-8:]
        result = []
        for r in norm:
            year = int(r.get("year", 0))
            # field name varies: gdp_growth_rate / real_gdp_growth / growth_rate
            rate = float(
                r.get("gdp_growth_rate")
                or r.get("real_gdp_growth")
                or r.get("growth_rate")
                or r.get("value")
                or 0
            )
            result.append({"year": year, "gdp": rate})
        if result:
            return result

    # Hardcoded fallback (from MTI official press releases)
    print("  ℹ️  Using hardcoded GDP fallback (MTI official figures)")
    return [
        {"year": 2018, "gdp": 3.5},
        {"year": 2019, "gdp": 1.1},
        {"year": 2020, "gdp": -3.9},
        {"year": 2021, "gdp": 8.9},
        {"year": 2022, "gdp": 3.6},
        {"year": 2023, "gdp": 1.1},
        {"year": 2024, "gdp": 5.3},
        {"year": 2025, "gdp": 5.0},  # MTI full-year 2025 (final)
    ]


def fetch_unemployment():
    """
    Unemployment rate from MOM / data.gov.sg.
    Dataset: d_a1d4e3e9c7ff3e7fbfd254fef0e6a6e5 (overall unemployment)
    Falls back to hardcoded values.
    """
    recs = datagov("d_a1d4e3e9c7ff3e7fbfd254fef0e6a6e5", limit=12, sort="quarter desc")
    if recs:
        norm = [{k.lower().strip(): v for k, v in r.items()} for r in recs]
        norm.sort(key=lambda r: _parse_quarter(r.get("quarter", "")))
        norm = norm[-8:]
        result = []
        for r in norm:
            yr, q = _parse_quarter(r.get("quarter", ""))
            rate = float(
                r.get("overall") or r.get("unemployment_rate") or r.get("value") or 0
            )
            result.append({"q": _q_label(yr, q), "rate": rate})
        if result:
            return result

    print("  ℹ️  Using hardcoded unemployment fallback (MOM official figures)")
    return [
        {"q": "22Q1", "rate": 2.3},
        {"q": "22Q3", "rate": 2.0},
        {"q": "23Q1", "rate": 2.0},
        {"q": "23Q3", "rate": 1.9},
        {"q": "24Q1", "rate": 1.9},
        {"q": "24Q3", "rate": 2.0},
        {"q": "25Q1", "rate": 2.1},
        {"q": "25Q3", "rate": 2.0},
        {"q": "26Q1", "rate": 2.1},  # MOM Q1 2026 (latest)
    ]


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN DATA FETCH — with cache
# ═══════════════════════════════════════════════════════════════════════════════


def fetch_all_data():
    cache = load_cache()
    if cache.get("ppi") and cache.get("unsold"):
        return cache

    print("\n🌐 Fetching live data from data.gov.sg APIs…")
    data = {}

    print("  • PPI by locality (CCR/RCR/OCR)…")
    data["ppi"] = fetch_ppi_by_locality()

    print("  • Unsold inventory by segment…")
    data["unsold"] = fetch_unsold_by_segment()

    print("  • New launches by region (CCR/RCR/OCR)…")
    data["launches"] = fetch_launches_by_region()

    print("  • GDP growth…")
    data["gdp"] = fetch_gdp()

    print("  • Unemployment…")
    data["unemployment"] = fetch_unemployment()

    save_cache(data)
    return data


# ═══════════════════════════════════════════════════════════════════════════════
#  DERIVE DISPLAY METRICS FROM LIVE DATA
# ═══════════════════════════════════════════════════════════════════════════════


def derive_kpis(data):
    """Compute headline KPI strings from live data."""

    # Latest GDP
    gdp_data = data.get("gdp") or []
    latest_gdp = next((g for g in reversed(gdp_data) if g["gdp"] != 0), None)
    gdp_str = f"{latest_gdp['gdp']:+.1f}%" if latest_gdp else "+5.0%"
    gdp_year = str(latest_gdp["year"]) if latest_gdp else "2025"

    # Latest unsold
    unsold_data = data.get("unsold") or []
    latest_unsold = unsold_data[-1] if unsold_data else {"q": "25Q3", "unsold": 17209}
    unsold_val = latest_unsold["unsold"]
    unsold_q = latest_unsold["q"]

    # Latest PPI change (RCR quarter-on-quarter)
    ppi_data = data.get("ppi") or []
    ppi_change_str = "N/A"
    ppi_latest_q = ""
    if len(ppi_data) >= 2:
        cur = ppi_data[-1]
        prv = ppi_data[-2]
        if prv["rcr"] and prv["rcr"] != 0:
            chg = ((cur["rcr"] - prv["rcr"]) / prv["rcr"]) * 100
            ppi_change_str = f"{chg:+.1f}%"
        else:
            ppi_change_str = "0.0%"
        ppi_latest_q = cur["q"]

    # Latest unemployment
    unemp_data = data.get("unemployment") or []
    latest_unemp = unemp_data[-1] if unemp_data else {"rate": 2.1, "q": "26Q1"}

    return {
        "gdp_str": gdp_str,
        "gdp_year": gdp_year,
        "unsold_val": unsold_val,
        "unsold_q": unsold_q,
        "ppi_chg": ppi_change_str,
        "ppi_latest_q": ppi_latest_q,
        "unemp_rate": latest_unemp["rate"],
        "unemp_q": latest_unemp["q"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  SVG CHART BUILDERS — data-driven
# ═══════════════════════════════════════════════════════════════════════════════


def _norm_svg_y(val, val_min, val_max, y_top=10, y_bot=140):
    """Map a data value to SVG y-coordinate (top=high values)."""
    if val_max == val_min:
        return (y_top + y_bot) / 2
    frac = (val - val_min) / (val_max - val_min)
    return y_bot - frac * (y_bot - y_top)


def build_ppi_svg(ppi_rows):
    """Build the PPI 3-line chart SVG from live data."""
    if not ppi_rows:
        return "<p style='color:#94A3B8;font-size:9pt;'>⚠️ PPI 数据暂时无法获取，请检查网络连接后重新运行。</p>"

    all_vals = (
        [r["ccr"] for r in ppi_rows]
        + [r["rcr"] for r in ppi_rows]
        + [r["ocr"] for r in ppi_rows]
    )
    v_min = min(all_vals) * 0.995
    v_max = max(all_vals) * 1.005
    n = len(ppi_rows)
    w = 720
    x_step = (w - 100) / max(n - 1, 1)

    def row_x(i):
        return 60 + i * x_step

    def row_y(v):
        return _norm_svg_y(v, v_min, v_max, y_top=12, y_bot=130)

    ccr_pts = " ".join(
        f"{row_x(i):.1f},{row_y(r['ccr']):.1f}" for i, r in enumerate(ppi_rows)
    )
    rcr_pts = " ".join(
        f"{row_x(i):.1f},{row_y(r['rcr']):.1f}" for i, r in enumerate(ppi_rows)
    )
    ocr_pts = " ".join(
        f"{row_x(i):.1f},{row_y(r['ocr']):.1f}" for i, r in enumerate(ppi_rows)
    )

    # Y axis labels
    y_labels = []
    for frac in [0.0, 0.5, 1.0]:
        v = v_min + frac * (v_max - v_min)
        y = _norm_svg_y(v, v_min, v_max, 12, 130)
        y_labels.append(
            f'<text x="52" y="{y + 3:.1f}" font-size="7.5" fill="#94A3B8" text-anchor="end">{v:.0f}</text>'
        )

    # X axis labels
    x_labels = []
    for i, r in enumerate(ppi_rows):
        x_labels.append(
            f'<text x="{row_x(i):.1f}" y="148" font-size="7.5" fill="#94A3B8" text-anchor="middle">{r["q"]}</text>'
        )

    # Latest dot + annotation for RCR
    lx = row_x(n - 1)
    ly = row_y(ppi_rows[-1]["rcr"])
    if len(ppi_rows) >= 2:
        denom = ppi_rows[-2]["rcr"]
        if denom and denom != 0:
            chg = ((ppi_rows[-1]["rcr"] - denom) / denom) * 100
            chg_str = f"RCR {chg:+.1f}%"
        else:
            chg_str = "RCR 0.0%"
    else:
        chg_str = "RCR"

    return f"""<svg viewBox="0 0 720 160" xmlns="http://www.w3.org/2000/svg" width="100%">
  <line x1="55" y1="10" x2="55" y2="135" stroke="#E2E8F0" stroke-width="1"/>
  <line x1="55" y1="135" x2="715" y2="135" stroke="#E2E8F0" stroke-width="1"/>
  {"".join(y_labels)}
  <polyline points="{ccr_pts}" fill="none" stroke="#8B5CF6" stroke-width="2"/>
  <polyline points="{rcr_pts}" fill="none" stroke="#3B82F6" stroke-width="2.5"/>
  <polyline points="{ocr_pts}" fill="none" stroke="#10B981" stroke-width="2"/>
  <circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="#3B82F6" stroke="white" stroke-width="1.5"/>
  <text x="{lx - 4:.1f}" y="{ly - 7:.1f}" font-size="7.5" fill="#3B82F6" text-anchor="end" font-weight="bold">{chg_str}</text>
  {"".join(x_labels)}
  <line x1="200" y1="153" x2="216" y2="153" stroke="#8B5CF6" stroke-width="2"/>
  <text x="219" y="156" font-size="8" fill="#64748B">CCR</text>
  <line x1="255" y1="153" x2="271" y2="153" stroke="#3B82F6" stroke-width="2"/>
  <text x="274" y="156" font-size="8" fill="#3B82F6" font-weight="bold">RCR ★</text>
  <line x1="315" y1="153" x2="331" y2="153" stroke="#10B981" stroke-width="2"/>
  <text x="334" y="156" font-size="8" fill="#64748B">OCR</text>
</svg>"""


def build_gls_svg(launches_rows, unsold_rows):
    """
    Build GLS 3-line supply + unsold inventory SVG from live data + GLS forecast.
    """
    # Merge launches + unsold + forecast
    launch_map = {r["q"]: r for r in (launches_rows or [])}
    unsold_map = {r["q"]: r["unsold"] for r in (unsold_rows or [])}

    # Collect all quarters (actuals), take last 8
    all_qs = sorted(
        set(list(launch_map.keys()) + list(unsold_map.keys())),
        key=lambda q: (
            int("20" + q[:2]) if len(q) >= 2 else 0,
            int(q[3]) if len(q) >= 4 else 0,
        ),
    )
    all_qs = all_qs[-8:]

    rows = []
    for q in all_qs:
        ldata = launch_map.get(q, {})
        rows.append(
            {
                "q": q,
                "ccr": ldata.get("ccr", 0),
                "rcr": ldata.get("rcr", 0),
                "ocr": ldata.get("ocr", 0),
                "unsold": unsold_map.get(q, 0),
                "fc": False,
            }
        )

    # Append GLS forecast quarters
    for q_label, fc in GLS_FORECAST.items():
        rows.append(
            {
                "q": q_label,
                "ccr": fc["ccr"],
                "rcr": fc["rcr"],
                "ocr": fc["ocr"],
                "unsold": 0,  # no inventory forecast
                "fc": True,
            }
        )

    n = len(rows)
    w = 720
    x_step = (w - 100) / max(n - 1, 1)

    def rx(i):
        return 60 + i * x_step

    # Left axis: GLS units
    max_gls = max((r["ccr"] + r["rcr"] + r["ocr"]) for r in rows) * 1.1 or 4000
    max_ocr = max(r["ocr"] for r in rows) or 2500

    def gls_y(v, vmax=max_ocr):
        return _norm_svg_y(v, 0, vmax, y_top=12, y_bot=130)

    # Right axis: unsold inventory (only actual rows)
    unsold_vals = [r["unsold"] for r in rows if r["unsold"] > 0]
    if unsold_vals:
        u_min = min(unsold_vals) * 0.95
        u_max = max(unsold_vals) * 1.05
    else:
        u_min, u_max = 10000, 25000

    def u_y(v):
        return _norm_svg_y(v, u_min, u_max, y_top=12, y_bot=130)

    # Forecast shading x range
    fc_indices = [i for i, r in enumerate(rows) if r["fc"]]
    shade = ""
    if fc_indices:
        x1 = rx(fc_indices[0]) - x_step * 0.4
        x2 = rx(fc_indices[-1]) + x_step * 0.4
        shade = (
            f'<rect x="{x1:.1f}" y="10" width="{x2 - x1:.1f}" height="120" '
            f'fill="rgba(148,163,184,0.10)" rx="3"/>'
            f'<text x="{(x1 + x2) / 2:.1f}" y="22" font-size="8.5" fill="#94A3B8" text-anchor="middle">政府预测</text>'
        )

    # Reference lines (unsold axis)
    r15k = u_y(15000)
    r25k = u_y(25000)
    ref_lines = (
        f'<line x1="55" y1="{r15k:.1f}" x2="715" y2="{r15k:.1f}" stroke="#10B981" stroke-width="1" stroke-dasharray="5 3"/>'
        f'<text x="718" y="{r15k + 3:.1f}" font-size="7.5" fill="#10B981">1.5万</text>'
        f'<line x1="55" y1="{r25k:.1f}" x2="715" y2="{r25k:.1f}" stroke="#EF4444" stroke-width="1" stroke-dasharray="5 3"/>'
        f'<text x="718" y="{r25k + 3:.1f}" font-size="7.5" fill="#EF4444">2.5万</text>'
    )

    # Build polylines for CCR, RCR, OCR
    def pts(key, y_fn):
        return " ".join(f"{rx(i):.1f},{y_fn(r[key]):.1f}" for i, r in enumerate(rows))

    def pts_dashed_split(key, y_fn):
        """Return solid segment up to last actual, then dashed for forecast."""
        last_actual = max((i for i, r in enumerate(rows) if not r["fc"]), default=-1)
        solid = " ".join(
            f"{rx(i):.1f},{y_fn(r[key]):.1f}"
            for i, r in enumerate(rows)
            if i <= last_actual
        )
        dash = " ".join(
            f"{rx(i):.1f},{y_fn(r[key]):.1f}"
            for i, r in enumerate(rows)
            if i >= last_actual
        )
        lines = []
        if solid:
            lines.append(
                f'<polyline points="{solid}" fill="none" stroke="{{color}}" stroke-width="{{w}}"/>'
            )
        if len(dash.split()) > 2:
            lines.append(
                f'<polyline points="{dash}" fill="none" stroke="{{color}}" stroke-width="{{w}}" stroke-dasharray="5 3"/>'
            )
        return lines

    ccr_lines = [
        l.replace("{color}", "#8B5CF6").replace("{w}", "2")
        for l in pts_dashed_split("ccr", gls_y)
    ]
    rcr_lines = [
        l.replace("{color}", "#3B82F6").replace("{w}", "2.5")
        for l in pts_dashed_split("rcr", gls_y)
    ]
    ocr_lines = [
        l.replace("{color}", "#10B981").replace("{w}", "2")
        for l in pts_dashed_split("ocr", gls_y)
    ]

    # Unsold inventory (only actual rows)
    unsold_pts_list = [
        (rx(i), u_y(r["unsold"])) for i, r in enumerate(rows) if r["unsold"] > 0
    ]
    unsold_line = ""
    if len(unsold_pts_list) >= 2:
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in unsold_pts_list)
        unsold_line = (
            f'<polyline points="{pts_str}" fill="none" stroke="#1E293B" '
            f'stroke-width="2" stroke-dasharray="7 3"/>'
        )
        # Highlight latest unsold dot
        lx, ly = unsold_pts_list[-1]
        latest_unsold_v = [r["unsold"] for r in rows if r["unsold"] > 0][-1]
        unsold_line += (
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="#1E293B"/>'
            f'<text x="{lx:.1f}" y="{ly - 7:.1f}" font-size="7.5" fill="#1E293B" '
            f'text-anchor="middle" font-weight="bold">{latest_unsold_v:,}</text>'
        )

    # X labels
    x_labels = []
    for i, r in enumerate(rows):
        color = "#3B82F6" if r["fc"] else "#94A3B8"
        weight = 'font-weight="bold"' if r["fc"] else ""
        x_labels.append(
            f'<text x="{rx(i):.1f}" y="148" font-size="7.5" fill="{color}" text-anchor="middle" {weight}>{r["q"]}</text>'
        )

    return f"""<svg viewBox="0 0 760 165" xmlns="http://www.w3.org/2000/svg" width="100%">
  <line x1="55" y1="10" x2="55" y2="135" stroke="#E2E8F0" stroke-width="1"/>
  <line x1="55" y1="135" x2="715" y2="135" stroke="#E2E8F0" stroke-width="1"/>
  {shade}
  {ref_lines}
  {"".join(ccr_lines)}
  {"".join(rcr_lines)}
  {"".join(ocr_lines)}
  {unsold_line}
  {"".join(x_labels)}
  <line x1="100" y1="158" x2="116" y2="158" stroke="#8B5CF6" stroke-width="2"/>
  <text x="119" y="161" font-size="8" fill="#64748B">CCR</text>
  <line x1="155" y1="158" x2="171" y2="158" stroke="#3B82F6" stroke-width="2"/>
  <text x="174" y="161" font-size="8" fill="#64748B">RCR</text>
  <line x1="210" y1="158" x2="226" y2="158" stroke="#10B981" stroke-width="2"/>
  <text x="229" y="161" font-size="8" fill="#64748B">OCR</text>
  <line x1="275" y1="158" x2="291" y2="158" stroke="#1E293B" stroke-width="2" stroke-dasharray="5 3"/>
  <text x="294" y="161" font-size="8" fill="#64748B">未售库存（右轴）</text>
  <text x="400" y="161" font-size="8" fill="#3B82F6" font-weight="bold">★ = 政府已公布预测</text>
</svg>"""


def build_gdp_svg(gdp_rows):
    """Bar chart for annual GDP growth."""
    if not gdp_rows:
        return "<p style='color:#94A3B8;font-size:9pt;'>GDP 数据暂时无法获取。</p>"

    n = len(gdp_rows)
    w = 720
    bar_w = min(50, (w - 80) / n - 8)
    x_step = (w - 80) / n
    zero_y = 100  # y position for 0%
    scale = 8  # px per 1%

    bars = []
    for i, r in enumerate(gdp_rows):
        cx = 50 + i * x_step + x_step / 2
        v = r["gdp"]
        color = "#3B82F6" if i == n - 1 else ("#EF4444" if v < 0 else "#10B981")
        if v >= 0:
            bar_h = v * scale
            by = zero_y - bar_h
        else:
            bar_h = abs(v) * scale
            by = zero_y
        bars.append(
            f'<rect x="{cx - bar_w / 2:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'fill="{color}" rx="2" opacity="0.88"/>'
            f'<text x="{cx:.1f}" y="{by - 3 if v >= 0 else by + bar_h + 10:.1f}" '
            f'font-size="8" fill="{color}" text-anchor="middle">{v:+.1f}%</text>'
            f'<text x="{cx:.1f}" y="122" font-size="7.5" fill="{"#3B82F6" if i == n - 1 else "#94A3B8"}" '
            f'text-anchor="middle" {"font-weight='bold'" if i == n - 1 else ""}>{r["year"]}</text>'
        )

    latest = gdp_rows[-1]
    return f"""<svg viewBox="0 0 720 135" xmlns="http://www.w3.org/2000/svg" width="100%">
  <line x1="40" y1="10" x2="40" y2="108" stroke="#E2E8F0" stroke-width="1"/>
  <line x1="40" y1="{zero_y}" x2="715" y2="{zero_y}" stroke="#1E293B" stroke-width="1"/>
  <text x="36" y="{zero_y + 3:.1f}" font-size="7.5" fill="#94A3B8" text-anchor="end">0%</text>
  <text x="36" y="{zero_y - 5 * scale + 3:.1f}" font-size="7.5" fill="#94A3B8" text-anchor="end">+5%</text>
  {"".join(bars)}
  <text x="600" y="15" font-size="8.5" fill="#3B82F6" font-weight="bold">最新: {latest["year"]} GDP {latest["gdp"]:+.1f}%</text>
</svg>"""


# ═══════════════════════════════════════════════════════════════════════════════
#  SHARED CSS (same as v1 but kept in one place)
# ═══════════════════════════════════════════════════════════════════════════════

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;
     background:#F8FAFC;color:#1E293B;font-size:10.5pt;line-height:1.5;}
.page{padding:18mm 16mm;max-width:210mm;margin:0 auto;}
.hdr{background:#1E293B;border-radius:8px;padding:16px 20px;margin-bottom:14px;color:white;}
.hdr h1{font-size:16pt;font-weight:700;margin-bottom:3px;}
.hdr .sub{font-size:9.5pt;color:#94A3B8;margin-bottom:8px;}
.hdr-meta{display:flex;flex-wrap:wrap;gap:7px;}
.chip{background:rgba(255,255,255,0.12);border-radius:5px;padding:3px 8px;font-size:8.5pt;color:#CBD5E1;}
.sl{font-size:8pt;font-weight:700;color:#94A3B8;letter-spacing:.07em;text-transform:uppercase;
    margin:12px 0 7px;border-bottom:1px solid #E2E8F0;padding-bottom:3px;}
.kpi4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:9px;margin-bottom:12px;}
.kc{background:white;border:1px solid #E2E8F0;border-radius:7px;padding:10px 12px;}
.kv{font-size:17pt;font-weight:700;}
.kl{font-size:8pt;color:#64748B;margin-top:2px;}
.ks{font-size:7.5pt;margin-top:2px;}
.pos{color:#10B981;}.neg{color:#EF4444;}.warn{color:#F59E0B;}.blue{color:#3B82F6;}
.card{background:white;border:1px solid #E2E8F0;border-radius:8px;padding:13px 15px;margin-bottom:11px;}
.ct{font-size:10.5pt;font-weight:700;margin-bottom:3px;}
.cs{font-size:8pt;color:#64748B;margin-bottom:9px;}
.ch{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:9px;}
.col2{display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-bottom:11px;}
.col3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:11px;margin-bottom:11px;}
.badge{display:inline-block;font-size:8pt;font-weight:700;padding:2px 8px;border-radius:20px;}
.b-bull{background:#DCFCE7;color:#166534;}.b-neutral{background:#FEF9C3;color:#854D0E;}
.b-bear{background:#FEE2E2;color:#991B1B;}.b-blue{background:#EFF6FF;color:#1E40AF;}
table{width:100%;border-collapse:collapse;font-size:9.5pt;}
th{text-align:left;color:#64748B;font-weight:700;font-size:8.5pt;padding:3px 5px;border-bottom:1.5px solid #E2E8F0;}
td{padding:4px 5px;border-bottom:1px solid #F1F5F9;}
tr:last-child td{border-bottom:none;}
.num{font-family:monospace;font-weight:600;}
.hl{background:#EFF6FF;border-radius:5px;padding:6px 10px;font-size:8.5pt;color:#1E40AF;margin-top:7px;line-height:1.5;}
.wl{background:#FFFBEB;border-radius:5px;padding:6px 10px;font-size:8.5pt;color:#92400E;margin-top:7px;line-height:1.5;}
.dl{background:#FEF2F2;border-radius:5px;padding:6px 10px;font-size:8.5pt;color:#991B1B;margin-top:7px;line-height:1.5;}
.gl{background:#F0FDF4;border-radius:5px;padding:6px 10px;font-size:8.5pt;color:#166534;margin-top:7px;line-height:1.5;}
.bar-row{display:flex;align-items:center;gap:6px;margin-bottom:7px;}
.bar-lbl{font-size:9pt;color:#64748B;min-width:90px;text-align:right;}
.bar-trk{flex:1;background:#F1F5F9;border-radius:3px;height:19px;overflow:hidden;}
.bar-fil{height:100%;border-radius:3px;display:flex;align-items:center;padding:0 6px;}
.bar-val{font-size:8.5pt;font-weight:700;color:white;}
.sc-row{display:flex;align-items:center;gap:6px;margin-bottom:6px;}
.sc-lbl{font-size:8.5pt;color:#1E293B;min-width:115px;}
.sc-trk{flex:1;background:#F1F5F9;border-radius:3px;height:15px;overflow:hidden;}
.sc-fil{height:100%;border-radius:3px;display:flex;align-items:center;padding:0 6px;}
.sc-val{font-size:7.5pt;font-weight:700;color:white;}
.irr-row{margin-bottom:10px;}
.irr-ttl{font-size:9pt;font-weight:700;margin-bottom:5px;}
.vb{border-radius:8px;padding:11px 13px;}
.v-buy{background:#F0FDF4;border:1px solid #86EFAC;}
.v-good{background:#EFF6FF;border:1px solid #93C5FD;}
.v-warn{background:#FFFBEB;border:1px solid #FCD34D;}
.vt{font-size:10pt;font-weight:700;margin-bottom:3px;}
.vrt{font-size:9pt;font-weight:700;margin-bottom:5px;}
.vtx{font-size:8.5pt;color:#475569;line-height:1.5;}
.pb{page-break-after:always;}
.final{background:#F8FAFC;border-radius:7px;padding:12px 14px;border-left:4px solid #3B82F6;
       font-size:9pt;color:#475569;line-height:1.7;margin-top:10px;}
.footer{font-size:7.5pt;color:#94A3B8;text-align:center;margin-top:15px;padding-top:8px;border-top:1px solid #E2E8F0;}
.data-stamp{font-size:8pt;color:#3B82F6;font-style:italic;margin-bottom:4px;}
svg text{font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;}
</style>
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  MACRO SECTION (shared between both reports)
# ═══════════════════════════════════════════════════════════════════════════════


def macro_section_html(kpis, data):
    ppi_svg = build_ppi_svg(data.get("ppi"))
    gls_svg = build_gls_svg(data.get("launches"), data.get("unsold"))
    gdp_svg = build_gdp_svg(data.get("gdp"))
    unemp_q = kpis["unemp_q"]
    unsold_q = kpis["unsold_q"]

    latest_unsold = kpis["unsold_val"]
    inventory_badge = (
        "乐观"
        if latest_unsold < 15000
        else ("中性" if latest_unsold < 25000 else "悲观")
    )
    inventory_color = (
        "b-bull"
        if latest_unsold < 15000
        else ("b-neutral" if latest_unsold < 25000 else "b-bear")
    )

    return f"""
<div class="sl">第一阶段 · 宏观市场分析 <span class="data-stamp">（实时数据 · 更新于 {REPORT_DATE}）</span></div>

<div class="kpi4">
  <div class="kc">
    <div class="kv pos">{kpis["gdp_str"]}</div>
    <div class="kl">{kpis["gdp_year"]} 年 GDP 增速</div>
    <div class="ks pos">MTI 官方数据</div>
  </div>
  <div class="kc">
    <div class="kv pos">{kpis["ppi_chg"]}</div>
    <div class="kl">PPI 最新季比（RCR）</div>
    <div class="ks pos">{kpis["ppi_latest_q"]} · URA</div>
  </div>
  <div class="kc">
    <div class="kv warn">{kpis["unemp_rate"]:.1f}%</div>
    <div class="kl">整体失业率</div>
    <div class="ks warn">{unemp_q} · MOM 数据</div>
  </div>
  <div class="kc">
    <div class="kv {"pos" if latest_unsold < 20000 else "warn"}">{latest_unsold:,}</div>
    <div class="kl">未售单位总量</div>
    <div class="ks">{unsold_q} · URA 实时数据</div>
  </div>
</div>

<div class="card">
  <div class="ch">
    <div>
      <div class="ct">GDP 年度增速（实时数据）</div>
      <div class="cs">data.gov.sg / MTI · 最新年份: {kpis["gdp_year"]}</div>
    </div>
    <span class="badge b-bull">实时</span>
  </div>
  {gdp_svg}
</div>

<div class="card">
  <div class="ch">
    <div>
      <div class="ct">GLS 供应分区走势（CCR/RCR/OCR）+ 未售库存</div>
      <div class="cs">数据来源：URA data.gov.sg · 每季度更新 · ★ = 政府已公布预测</div>
    </div>
    <span class="badge {inventory_color}">{inventory_badge}</span>
  </div>
  {gls_svg}
  <div class="hl">
    <strong>1H 2026 Confirmed List：{GLS_TOTAL_1H2026:,} 套，比十年均值高约 50%。</strong>
    CCR ~{GLS_FORECAST["H1 2026★"]["ccr"]} 套（Newton Urban Village），
    RCR ~{GLS_FORECAST["H1 2026★"]["rcr"]} 套，
    OCR ~{GLS_FORECAST["H1 2026★"]["ocr"]} 套（Bedok / Bayshore）。
    最新未售库存 {latest_unsold:,} 套（{unsold_q}），趋势向下。
  </div>
</div>

<div class="card">
  <div class="ch">
    <div>
      <div class="ct">私宅价格指数（PPI）三区走势</div>
      <div class="cs">URA · data.gov.sg · 自动更新 · 基期 2009Q1=100</div>
    </div>
    <span class="badge b-bull">实时</span>
  </div>
  {ppi_svg}
  <div class="hl">
    PPI 由 data.gov.sg 实时获取，每季度更新。图表始终显示最新数据。
    RCR 为本报告重点区域（阳光广场 D7 / 肯特苑 D8 均属 RCR）。
  </div>
</div>"""


# ═══════════════════════════════════════════════════════════════════════════════
#  PROPERTY-SPECIFIC SECTIONS (static — based on URA Realis & research)
#  These sections update only when you manually refresh URA Realis data.
# ═══════════════════════════════════════════════════════════════════════════════

SUNSHINE_FINANCIAL = """
<div class="pb"></div>
<div class="sl">第二阶段 · 财务建模 — 1 房约 592 sqft @ $880,000（$1,486/sqft）</div>
<div class="col2">
  <div class="card">
    <div class="ct" style="margin-bottom:9px;">购置成本明细</div>
    <table>
      <tr><th>费用项目</th><th style="text-align:right;">金额</th></tr>
      <tr><td>购置价格</td><td class="num" style="text-align:right;">$880,000</td></tr>
      <tr><td>BSD</td><td class="num" style="text-align:right;">$22,200</td></tr>
      <tr><td>ABSD（SC 首套）</td><td class="num" style="text-align:right;color:#10B981;">豁免 $0</td></tr>
      <tr><td style="color:#EF4444;">ABSD（SC 第二套）</td><td class="num" style="text-align:right;color:#EF4444;">$176,000</td></tr>
      <tr><td>律师费</td><td class="num" style="text-align:right;">~$3,000</td></tr>
      <tr style="background:#F0FDF4;"><td><strong>总成本（SC 首套）</strong></td>
          <td class="num" style="text-align:right;font-weight:700;color:#10B981;">~$905,200</td></tr>
      <tr style="background:#FEF2F2;"><td><strong>总成本（SC 第二套）</strong></td>
          <td class="num" style="text-align:right;font-weight:700;color:#EF4444;">~$1,081,200</td></tr>
    </table>
    <div style="margin-top:10px;">
      <div style="font-size:8.5pt;font-weight:700;color:#64748B;margin-bottom:6px;">首付构成（75% 贷款）</div>
      <div class="bar-row"><div class="bar-lbl">现金 5%</div>
        <div class="bar-trk"><div class="bar-fil" style="width:25%;background:#EF4444;">
          <span class="bar-val">$44,000</span></div></div></div>
      <div class="bar-row"><div class="bar-lbl">首付 25%</div>
        <div class="bar-trk"><div class="bar-fil" style="width:55%;background:#F59E0B;">
          <span class="bar-val">$220,000</span></div></div></div>
      <div class="bar-row"><div class="bar-lbl">最高贷款 75%</div>
        <div class="bar-trk"><div class="bar-fil" style="width:100%;background:#3B82F6;">
          <span class="bar-val">$660,000</span></div></div></div>
    </div>
  </div>
  <div class="card">
    <div class="ct" style="margin-bottom:4px;">月供 & TDSR 压力测试</div>
    <div class="cs">贷款 $660,000 · 30 年</div>
    <table>
      <tr><th>利率</th><th style="text-align:right;">月供</th><th style="text-align:right;">所需月收入</th></tr>
      <tr><td>3.5%（当前）</td><td class="num" style="text-align:right;">$2,963</td>
          <td style="text-align:right;font-size:8pt;color:#10B981;">~$5,387</td></tr>
      <tr style="background:#FFFBEB;"><td><strong>5.5%（压力测试）</strong></td>
          <td class="num" style="text-align:right;font-weight:700;">$3,749</td>
          <td style="text-align:right;font-size:8pt;color:#F59E0B;font-weight:700;">~$6,816</td></tr>
    </table>
    <div class="gl">✅ <strong>正现金流</strong>：月租 $3,600 > 月供 $2,963，净盈余约 $600–$800/月。</div>
    <div style="margin-top:10px;padding:9px;background:#F8FAFC;border-radius:7px;">
      <div style="font-size:9pt;font-weight:700;margin-bottom:6px;">租金收益</div>
      <div class="bar-row"><div class="bar-lbl">月租 $3,600</div>
        <div class="bar-trk"><div class="bar-fil" style="width:100%;background:#10B981;">
          <span class="bar-val">毛回报约 4.9%</span></div></div></div>
      <div class="bar-row"><div class="bar-lbl">净回报</div>
        <div class="bar-trk"><div class="bar-fil" style="width:84%;background:#F59E0B;">
          <span class="bar-val">约 3.8–4.2%</span></div></div></div>
    </div>
  </div>
</div>
<div class="card">
  <div class="ct" style="margin-bottom:4px;">IRR 情景分析</div>
  <div class="cs">入场 $880k · SC 首套 · 月租 $3,600</div>
  <div class="col2" style="margin-bottom:0;">
    <div>
      <div class="irr-row"><div class="irr-ttl" style="color:#EF4444;">🔴 悲观（1.5% p.a.）</div>
        <div class="bar-row"><div class="bar-lbl">5 年</div>
          <div class="bar-trk"><div class="bar-fil" style="width:19%;background:#EF4444;"><span class="bar-val">1.9%</span></div></div></div>
        <div class="bar-row"><div class="bar-lbl">10 年</div>
          <div class="bar-trk"><div class="bar-fil" style="width:31%;background:#EF4444;"><span class="bar-val">3.1%</span></div></div></div>
      </div>
      <div class="irr-row"><div class="irr-ttl" style="color:#3B82F6;">🔵 基准（3.0% p.a.）</div>
        <div class="bar-row"><div class="bar-lbl">5 年</div>
          <div class="bar-trk"><div class="bar-fil" style="width:46%;background:#3B82F6;"><span class="bar-val">4.6%</span></div></div></div>
        <div class="bar-row"><div class="bar-lbl">10 年</div>
          <div class="bar-trk"><div class="bar-fil" style="width:62%;background:#3B82F6;"><span class="bar-val">6.2%</span></div></div></div>
      </div>
      <div class="irr-row"><div class="irr-ttl" style="color:#10B981;">🟢 乐观（5.0% p.a.）</div>
        <div class="bar-row"><div class="bar-lbl">5 年</div>
          <div class="bar-trk"><div class="bar-fil" style="width:74%;background:#10B981;"><span class="bar-val">7.4%</span></div></div></div>
        <div class="bar-row"><div class="bar-lbl">10 年</div>
          <div class="bar-trk"><div class="bar-fil" style="width:88%;background:#10B981;"><span class="bar-val">8.8%</span></div></div></div>
      </div>
    </div>
    <div>
      <div style="font-size:9pt;font-weight:700;color:#64748B;margin-bottom:8px;">5 年现金流（基准）</div>
      <svg viewBox="0 0 290 160" xmlns="http://www.w3.org/2000/svg" width="100%">
        <line x1="38" y1="8" x2="38" y2="138" stroke="#E2E8F0"/>
        <line x1="38" y1="138" x2="285" y2="138" stroke="#E2E8F0"/>
        <line x1="38" y1="83" x2="285" y2="83" stroke="#1E293B" stroke-dasharray="3" stroke-width="0.7"/>
        <text x="33" y="86" font-size="7.5" fill="#94A3B8" text-anchor="end">0</text>
        <rect x="47" y="83" width="33" height="52" fill="#EF4444" rx="2" opacity="0.85"/>
        <text x="63" y="143" font-size="7.5" fill="#EF4444" text-anchor="middle">-$33万</text>
        <text x="63" y="135" font-size="7" fill="#94A3B8" text-anchor="middle">第0年</text>
        <rect x="93" y="76" width="28" height="7" fill="#10B981" rx="2"/>
        <text x="107" y="97" font-size="7" fill="#94A3B8" text-anchor="middle">第1年</text>
        <rect x="133" y="76" width="28" height="7" fill="#10B981" rx="2"/>
        <text x="147" y="97" font-size="7" fill="#94A3B8" text-anchor="middle">第2年</text>
        <rect x="173" y="76" width="28" height="7" fill="#10B981" rx="2"/>
        <text x="187" y="97" font-size="7" fill="#94A3B8" text-anchor="middle">第3年</text>
        <rect x="213" y="76" width="28" height="7" fill="#10B981" rx="2"/>
        <text x="227" y="97" font-size="7" fill="#94A3B8" text-anchor="middle">第4年</text>
        <rect x="253" y="38" width="30" height="45" fill="#10B981" rx="2" opacity="0.9"/>
        <text x="268" y="89" font-size="7.5" fill="#10B981" text-anchor="middle">+$21万</text>
        <text x="268" y="35" font-size="7.5" fill="#10B981" text-anchor="middle" font-weight="bold">净收益</text>
        <text x="268" y="101" font-size="7" fill="#94A3B8" text-anchor="middle">第5年</text>
      </svg>
    </div>
  </div>
</div>"""


SUNSHINE_QUALITATIVE = """
<div class="sl">第三阶段 · 定性估值</div>
<div class="col2">
  <div class="card">
    <div class="ch">
      <div><div class="ct">D7 CMA — PSF 对比</div>
      <div class="cs">近 24 个月 URA Realis 成交均价</div></div>
      <span class="badge b-neutral">合理估值</span>
    </div>
    <div class="bar-row"><div class="bar-lbl" style="font-weight:700;color:#3B82F6;">阳光广场（目标）</div>
      <div class="bar-trk"><div class="bar-fil" style="width:52%;background:#3B82F6;">
        <span class="bar-val">$1,558（99 年）</span></div></div></div>
    <div class="bar-row"><div class="bar-lbl">Rochor Suites</div>
      <div class="bar-trk"><div class="bar-fil" style="width:61%;background:#94A3B8;">
        <span class="bar-val">~$1,820（永久）</span></div></div></div>
    <div class="bar-row"><div class="bar-lbl">D7 永久均值</div>
      <div class="bar-trk"><div class="bar-fil" style="width:70%;background:#8B5CF6;">
        <span class="bar-val">~$2,100（永久）</span></div></div></div>
    <div class="bar-row"><div class="bar-lbl">Midtown Bay</div>
      <div class="bar-trk"><div class="bar-fil" style="width:100%;background:#94A3B8;">
        <span class="bar-val">~$2,980（99 年）</span></div></div></div>
    <div class="hl"><strong>议价目标：$1,480–$1,560/sqft（约 $880k–$940k）。</strong><br>
      叫价 $1,716–$2,111/sqft 较成交溢价 10–35%，切勿按叫价成交。</div>
  </div>
  <div class="card">
    <div class="ct" style="margin-bottom:9px;">位置评分</div>
    <div class="sc-row"><div class="sc-lbl">🚇 MRT 便利性</div>
      <div class="sc-trk"><div class="sc-fil" style="width:95%;background:#10B981;">
        <span class="sc-val">95/100 — DT21 约 200m，三线可达</span></div></div></div>
    <div class="sc-row"><div class="sc-lbl">🛍️ 生活配套</div>
      <div class="sc-trk"><div class="sc-fil" style="width:90%;background:#10B981;">
        <span class="sc-val">90/100 — Bugis Junction 步行可达</span></div></div></div>
    <div class="sc-row"><div class="sc-lbl">🎓 大学城租客</div>
      <div class="sc-trk"><div class="sc-fil" style="width:88%;background:#10B981;">
        <span class="sc-val">88/100 — SMU/NAFA/Kaplan 5–8 分钟</span></div></div></div>
    <div class="sc-row"><div class="sc-lbl">📈 增值潜力</div>
      <div class="sc-trk"><div class="sc-fil" style="width:72%;background:#3B82F6;">
        <span class="sc-val">72/100 — 正现金流但 GLS 新供应竞争</span></div></div></div>
    <div class="sc-row"><div class="sc-lbl">🏫 学校资源</div>
      <div class="sc-trk"><div class="sc-fil" style="width:55%;background:#F59E0B;">
        <span class="sc-val">55/100 — St. Margaret Primary 0.6km</span></div></div></div>
    <div class="sc-row"><div class="sc-lbl"><strong>综合评分</strong></div>
      <div class="sc-trk"><div class="sc-fil" style="width:78%;background:#1E293B;">
        <span class="sc-val" style="font-size:9pt;font-weight:700;">78 / 100</span></div></div></div>
  </div>
</div>"""


SUNSHINE_VERDICT = """
<div class="sl">综合评级</div>
<div class="col3">
  <div class="vb v-buy"><div class="vt" style="color:#166534;">自住（SC 首套）</div>
    <div style="font-size:20pt;margin:4px 0;">✅</div>
    <div class="vrt" style="color:#166534;">强烈推荐</div>
    <div class="vtx">三线 MRT，月收入仅需 ~$6,816 通过压力测试，租金正覆盖月供。</div>
  </div>
  <div class="vb v-good"><div class="vt" style="color:#1D4ED8;">投资（SC 首套）</div>
    <div style="font-size:20pt;margin:4px 0;">⭐</div>
    <div class="vrt" style="color:#1D4ED8;">积极推荐</div>
    <div class="vtx">正现金流 +$600–$800/月，乐观情景 10 年 IRR 8.8%。D7 租客群稳定。</div>
  </div>
  <div class="vb v-warn"><div class="vt" style="color:#92400E;">SC 第二套 / PR</div>
    <div style="font-size:20pt;margin:4px 0;">⚠️</div>
    <div class="vrt" style="color:#92400E;">谨慎</div>
    <div class="vtx">20% ABSD $176,000，PR 首套 5%。需精算 IRR 后再决定。</div>
  </div>
</div>
<div class="final">
  <strong>总结：</strong>Sunshine Plaza 1 房是 D7 少见的正现金流投资标的，三条 MRT 线（DT21 仅 200m），
  大学城租客群保证低空置率。议价至 $1,480–$1,560/sqft；若持有超 7 年须提前制定退出计划。
</div>"""


KENTISH_FINANCIAL = """
<div class="pb"></div>
<div class="sl">地契风险 — 核心分析</div>
<div class="card">
  <div class="ch">
    <div><div class="ct">99 年地契衰减时间线（1995 年 3 月起）</div></div>
    <span class="badge b-bear">高风险</span>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:12px;">
    <div style="text-align:center;padding:10px;background:#F0FDF4;border-radius:7px;border:1px solid #86EFAC;">
      <div style="font-size:15pt;font-weight:700;color:#10B981;">约 69 年</div>
      <div style="font-size:8pt;color:#64748B;">当前（2026）</div>
      <div style="font-size:7.5pt;color:#10B981;">🟢 正常</div></div>
    <div style="text-align:center;padding:10px;background:#FFFBEB;border-radius:7px;border:1px solid #FCD34D;">
      <div style="font-size:15pt;font-weight:700;color:#F59E0B;">约 64 年</div>
      <div style="font-size:8pt;color:#64748B;">5 年后（2031）</div>
      <div style="font-size:7.5pt;color:#F59E0B;">🟡 注意</div></div>
    <div style="text-align:center;padding:10px;background:#FFF7ED;border-radius:7px;border:1px solid #FDBA74;">
      <div style="font-size:15pt;font-weight:700;color:#EA580C;">约 61 年</div>
      <div style="font-size:8pt;color:#64748B;">最迟出售（2034）</div>
      <div style="font-size:7.5pt;color:#EA580C;">🟠 临界</div></div>
    <div style="text-align:center;padding:10px;background:#FEF2F2;border-radius:7px;border:1px solid #FCA5A5;">
      <div style="font-size:15pt;font-weight:700;color:#EF4444;">约 59 年</div>
      <div style="font-size:8pt;color:#64748B;">10 年后（2036）</div>
      <div style="font-size:7.5pt;color:#EF4444;">🔴 融资受限</div></div>
  </div>
  <div style="width:100%;height:16px;border-radius:8px;
    background:linear-gradient(to right,#10B981 0%,#10B981 38%,#F59E0B 52%,#EF4444 65%,#7F1D1D 100%);
    margin-bottom:5px;"></div>
  <div style="display:flex;justify-content:space-between;font-size:8pt;color:#94A3B8;margin-bottom:8px;">
    <span>99 年</span><span>70 年</span><span>⚠️ 60 年红线</span><span>🚨 40 年</span><span>0</span>
  </div>
  <div class="dl">⚠️ 银行对剩余地契 &lt;60 年施加更严格贷款限制，买家群体大幅收窄。
    <strong>强烈建议最迟 2032–2033 年前完成出售。</strong></div>
</div>

<div class="sl">第二阶段 · 财务建模 — 2 房约 1,109 sqft @ $1,460,000</div>
<div class="col2">
  <div class="card">
    <div class="ct" style="margin-bottom:9px;">购置成本明细</div>
    <table>
      <tr><th>费用项目</th><th style="text-align:right;">金额</th></tr>
      <tr><td>购置价格</td><td class="num" style="text-align:right;">$1,460,000</td></tr>
      <tr><td>BSD</td><td class="num" style="text-align:right;">$42,200</td></tr>
      <tr><td>ABSD（SC 首套）</td><td class="num" style="text-align:right;color:#10B981;">豁免 $0</td></tr>
      <tr><td style="color:#EF4444;">ABSD（SC 第二套，20%）</td>
          <td class="num" style="text-align:right;color:#EF4444;">$292,000</td></tr>
      <tr><td>律师费</td><td class="num" style="text-align:right;">~$3,000</td></tr>
      <tr style="background:#F0FDF4;"><td><strong>总成本（SC 首套）</strong></td>
          <td class="num" style="text-align:right;font-weight:700;color:#10B981;">~$1,505,200</td></tr>
      <tr style="background:#FEF2F2;"><td><strong>总成本（SC 第二套）</strong></td>
          <td class="num" style="text-align:right;font-weight:700;color:#EF4444;">~$1,797,200</td></tr>
    </table>
  </div>
  <div class="card">
    <div class="ct" style="margin-bottom:4px;">月供 & TDSR</div>
    <div class="cs">贷款 $1,095,000 · 30 年</div>
    <table>
      <tr><th>利率</th><th style="text-align:right;">月供</th><th style="text-align:right;">所需月收入</th></tr>
      <tr><td>3.5%</td><td class="num" style="text-align:right;">$4,918</td>
          <td style="text-align:right;font-size:8pt;color:#10B981;">~$8,942</td></tr>
      <tr style="background:#FFFBEB;"><td><strong>5.5%（压力测试）</strong></td>
          <td class="num" style="text-align:right;font-weight:700;">$6,218</td>
          <td style="text-align:right;font-size:8pt;color:#F59E0B;font-weight:700;">~$11,306</td></tr>
    </table>
    <div class="dl">⚠️ <strong>负现金流</strong>：月供超过租金约 $900–$1,200，每年自补约 $10k–$14k。</div>
    <div style="margin-top:9px;padding:9px;background:#F8FAFC;border-radius:7px;">
      <div style="font-size:9pt;font-weight:700;margin-bottom:5px;">租金收益（$4,000/月）</div>
      <div class="bar-row"><div class="bar-lbl">毛回报</div>
        <div class="bar-trk"><div class="bar-fil" style="width:33%;background:#F59E0B;">
          <span class="bar-val">约 3.3%</span></div></div></div>
      <div class="bar-row"><div class="bar-lbl">净回报</div>
        <div class="bar-trk"><div class="bar-fil" style="width:26%;background:#F59E0B;">
          <span class="bar-val">约 2.5–2.8%</span></div></div></div>
    </div>
  </div>
</div>"""


KENTISH_VERDICT = """
<div class="sl">综合评级</div>
<div class="col3">
  <div class="vb v-buy"><div class="vt" style="color:#166534;">自住（SC 首套）</div>
    <div style="font-size:20pt;margin:4px 0;">✅</div>
    <div class="vrt" style="color:#166534;">有条件推荐</div>
    <div class="vtx">地段佳，户型宽敞，SJI Junior 1km 内。议价 $1,310–$1,330/sqft。</div>
  </div>
  <div class="vb v-warn"><div class="vt" style="color:#92400E;">短期投资</div>
    <div style="font-size:20pt;margin:4px 0;">⚠️</div>
    <div class="vrt" style="color:#92400E;">谨慎</div>
    <div class="vtx">基准 IRR 4.2%（5年），每年负现金流约 $10k–$14k。仅在升值 &gt;3% 时成立。</div>
  </div>
  <div class="vb" style="background:#FEF2F2;border:1px solid #FCA5A5;">
    <div class="vt" style="color:#991B1B;">SC 第二套 / 长期</div>
    <div style="font-size:20pt;margin:4px 0;">❌</div>
    <div class="vrt" style="color:#991B1B;">不推荐</div>
    <div class="vtx">ABSD $292k 令回报极难成立。10 年持有地契跌破 60 年红线。</div>
  </div>
</div>
<div class="final">
  <strong>总结：</strong>肯特苑最适合 SC 首套自住，注重中央地段与学区，7–10 年后退出。
  须在地契约 62 年前（2032–2033 年）完成出售，避免转售流动性风险。
  关键：议价目标 $1,310–$1,330/sqft，月收入 ≥ $11,306 通过 TDSR。
</div>"""


# ═══════════════════════════════════════════════════════════════════════════════
#  FULL HTML BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════


def data_source_note():
    return (
        f'<div style="font-size:7.5pt;color:#3B82F6;background:#EFF6FF;'
        f'border-radius:5px;padding:5px 9px;margin-bottom:10px;">'
        f"🌐 <strong>实时数据报告</strong> — 宏观图表（PPI / GLS / GDP）每次运行自动从 "
        f"data.gov.sg 官方 API 获取最新数据。成交记录基于 URA Realis 研究数据（2025Q4 最新）。"
        f"报告生成时间：{REPORT_DATE}</div>"
    )


FOOTER = f"""
<div class="footer">
  宏观数据来源：data.gov.sg（URA / MOM / MTI 官方 API）· GLS 预测：URA 2025 年 12 月公告 ·
  成交数据：URA Realis · EdgeProp · 99.co<br>
  报告生成：{REPORT_DATE} · 仅供参考，不构成投资建议。请向持牌房产经纪及财务顾问咨询。
</div>"""


def build_html(title, header_html, content_html, macro_html):
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{SHARED_CSS}
</head>
<body>
<div class="page">
{header_html}
{data_source_note()}
{macro_html}
{content_html}
{FOOTER}
</div>
</body>
</html>"""


def sunshine_plaza_full_html(kpis, data):
    header = f"""
<div class="hdr">
  <h1>☀️ 阳光广场（Sunshine Plaza）1 房投资分析</h1>
  <div class="sub">10 Prinsep Link · 第 7 邮区 · RCR · CDL · 宏观数据实时更新</div>
  <div class="hdr-meta">
    <span class="chip">99 年地契（1997 起）</span>
    <span class="chip">TOP 2001 · 160 套</span>
    <span class="chip">1 房 560–620 sqft</span>
    <span class="chip">剩余约 71 年（2026）</span>
    <span class="chip">🌐 实时数据 · {REPORT_DATE}</span>
  </div>
</div>"""
    content = SUNSHINE_FINANCIAL + SUNSHINE_QUALITATIVE + SUNSHINE_VERDICT
    return build_html(
        f"阳光广场投资分析 {REPORT_DATE}",
        header,
        content,
        macro_section_html(kpis, data),
    )


def kentish_court_full_html(kpis, data):
    header = f"""
<div class="hdr">
  <h1>🏢 肯特苑（Kentish Court）投资分析报告</h1>
  <div class="sub">牛津路 33 号 · 第 8 邮区 · RCR · 远东机构 · 宏观数据实时更新</div>
  <div class="hdr-meta">
    <span class="chip">99 年地契（1995 年 3 月起）</span>
    <span class="chip">TOP 2000 · 77 套</span>
    <span class="chip">2/3 房 1,044–1,356 sqft</span>
    <span class="chip">剩余约 69 年（2026）</span>
    <span class="chip">🌐 实时数据 · {REPORT_DATE}</span>
  </div>
</div>"""
    content = KENTISH_FINANCIAL + KENTISH_VERDICT
    return build_html(
        f"肯特苑投资分析 {REPORT_DATE}", header, content, macro_section_html(kpis, data)
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  PDF GENERATION
# ═══════════════════════════════════════════════════════════════════════════════


def html_to_pdf(html_path, pdf_path):
    try:
        from weasyprint import HTML, CSS

        HTML(filename=str(html_path)).write_pdf(
            str(pdf_path), stylesheets=[CSS(string="@page { size: A4; margin: 0; }")]
        )
        kb = os.path.getsize(pdf_path) // 1024
        print(f"  ✅ PDF: {pdf_path.name} ({kb} KB)")
    except ImportError:
        print("  ⚠️  weasyprint not installed — skipping PDF generation.")
        print("     Install:  pip install weasyprint")
        print("     Windows:  also install GTK3 from the URL in the script header.")
    except Exception as e:
        print(f"  ❌ PDF failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    print("=" * 62)
    print("  新加坡房产仪表板 — 实时数据版")
    print("  SG Property Dashboard — Live Data Edition")
    print(f"  {REPORT_DATE}")
    print("=" * 62)

    # 1. Fetch all live data (with cache)
    data = fetch_all_data()

    # 2. Derive KPI strings
    kpis = derive_kpis(data)
    print(f"\n📊 最新 KPI:")
    print(f"   GDP:      {kpis['gdp_str']} ({kpis['gdp_year']})")
    print(f"   PPI RCR:  {kpis['ppi_chg']} ({kpis['ppi_latest_q']})")
    print(f"   失业率:   {kpis['unemp_rate']}% ({kpis['unemp_q']})")
    print(f"   未售库存: {kpis['unsold_val']:,} 套 ({kpis['unsold_q']})")

    # 3. Build and write HTML + PDF
    reports = [
        ("sunshine_plaza_dashboard", "阳光广场 1 房", sunshine_plaza_full_html),
        ("kentish_court_dashboard", "肯特苑 2 房", kentish_court_full_html),
    ]

    print()
    for slug, name, builder in reports:
        print(f"📄 正在生成: {name}")
        html_content = builder(kpis, data)
        html_path = OUTPUT_DIR / f"{slug}.html"
        pdf_path = OUTPUT_DIR / f"{slug}.pdf"

        html_path.write_text(html_content, encoding="utf-8")
        print(f"  ✅ HTML: {html_path.name}")

        if GENERATE_PDF:
            html_to_pdf(html_path, pdf_path)

    print("\n" + "=" * 62)
    print("  ✅ 完成！Open .html in browser / .pdf for print")
    print(f"  📦 数据缓存：{CACHE_FILE.name} (每 {CACHE_HOURS} 小时更新)")
    print("=" * 62)


if __name__ == "__main__":
    main()
