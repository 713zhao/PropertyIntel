from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
from typing import Optional
import json
import datetime
import re
import urllib.request
import urllib.error
import urllib.parse
import ssl
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Property Intelligence API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

base_dir = os.path.dirname(os.path.abspath(__file__))
# Priority: ENV variable (for Fly.io volume) > Default local path
DB_PATH = os.getenv("DATABASE_URL", os.path.join(base_dir, "data", "property_data.db"))


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def read_root():
    return {"message": "Property Intelligence API is running"}


@app.get("/api/hdb-index")
def get_hdb_index():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM hdb_resale_index ORDER BY quarter ASC"
        df = pd.read_sql_query(query, conn)
        return df.to_dict(orient="records")
    finally:
        conn.close()


@app.get("/api/hdb-transactions")
def get_hdb_transactions(
    town: Optional[str] = None, flat_type: Optional[str] = None, limit: int = 100
):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM hdb_transactions WHERE 1=1"
        params = []
        if town:
            query += " AND town = ?"
            params.append(town)
        if flat_type:
            query += " AND flat_type = ?"
            params.append(flat_type)

        query += f" ORDER BY month DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn, params=params)
        return df.to_dict(orient="records")
    finally:
        conn.close()


@app.get("/api/population")
def get_population():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM population_indicators ORDER BY year ASC"
        df = pd.read_sql_query(query, conn)
        return df.to_dict(orient="records")
    finally:
        conn.close()


@app.get("/api/private-index")
def get_private_index():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM private_property_index ORDER BY quarter ASC"
        df = pd.read_sql_query(query, conn)
        return df.to_dict(orient="records")
    finally:
        conn.close()


@app.get("/api/rental-index")
def get_rental_index():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM private_rental_index ORDER BY quarter ASC"
        df = pd.read_sql_query(query, conn)
        return df.to_dict(orient="records")
    finally:
        conn.close()


@app.get("/api/macro-insights")
def get_macro_insights():
    conn = get_db_connection()
    try:
        # Get HDB Index (Quarterly)
        hdb_df = pd.read_sql_query(
            "SELECT quarter, [index] as hdb_index FROM hdb_resale_index", conn
        )
        # Get Private Index (Quarterly) - All Residential
        priv_df = pd.read_sql_query(
            "SELECT quarter, [index] as private_index FROM private_property_index WHERE property_type = 'All Residential'",
            conn,
        )
        # Get Rental Index (Quarterly) - All Residential
        rental_df = pd.read_sql_query(
            "SELECT quarter, [index] as rental_index FROM private_rental_index WHERE property_type = 'All Residential'",
            conn,
        )

        # Merge Indices
        indices = pd.merge(hdb_df, priv_df, on="quarter", how="outer")
        indices = pd.merge(indices, rental_df, on="quarter", how="outer")

        # Get Income (Annual)
        income_df = pd.read_sql_query(
            "SELECT Dollar as year, ResidentHouseholds_Median1 as median_income FROM household_income",
            conn,
        )

        # Get Population (Annual) - Wide to Long
        pop_df_wide = pd.read_sql_query(
            "SELECT * FROM population_indicators WHERE DataSeries = 'Total Population'",
            conn,
        )
        pop_df = pop_df_wide.melt(
            id_vars=["DataSeries"], var_name="year", value_name="total_population"
        )
        pop_df["year"] = pd.to_numeric(pop_df["year"], errors="coerce")
        pop_df = pop_df.dropna(subset=["year"])
        pop_df["year"] = pop_df["year"].astype(int)

        # Extract year from quarter for joining
        indices["year"] = indices["quarter"].str.split("-").str[0].astype(int)

        # Merge all
        result = pd.merge(indices, income_df, on="year", how="left")
        result = pd.merge(result, pop_df, on="year", how="left")

        # Sort by quarter
        result = result.sort_values("quarter")

        # Limit to last 50 years to keep it clean
        result = result.tail(200)

        # Calculate derived metrics
        # 1. HDB vs Private Gap
        result["price_gap"] = (result["private_index"] / result["hdb_index"]).round(2)

        # 2. Yield Proxy (Rental Index / Price Index)
        result["yield_proxy"] = (
            result["rental_index"] / result["private_index"] * 100
        ).round(2)

        # 3. Affordability (Income to Price Index)
        # Higher median_income / index means better affordability
        result["affordability_index"] = (
            result["median_income"] / result["private_index"]
        ).round(2)

        # Convert NaN to None for JSON compatibility
        return result.replace({pd.NA: None, float("nan"): None}).to_dict(
            orient="records"
        )
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return {"error": str(e)}
    finally:
        conn.close()


@app.get("/api/land-intelligence")
def get_land_intelligence():
    conn = get_db_connection()
    try:
        # Get GLS Data
        gls_df = pd.read_sql_query(
            "SELECT * FROM gls_residential ORDER BY year ASC", conn
        )
        # Get New Launch Correlation
        launch_df = pd.read_sql_query(
            "SELECT * FROM new_launches ORDER BY year ASC", conn
        )

        return {
            "gls_history": gls_df.to_dict(orient="records"),
            "launch_correlation": launch_df.to_dict(orient="records"),
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


@app.get("/api/new-launches")
def get_new_launches():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM new_launches ORDER BY year DESC"
        df = pd.read_sql_query(query, conn)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


@app.get("/api/transactions")
def get_transactions(project: Optional[str] = None, limit: int = 100):
    conn = get_db_connection()
    try:
        # Check if ura_transactions exists
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ura_transactions'"
        )
        if cursor.fetchone():
            query = f"SELECT project, price, 'N/A' as profit, transaction_date as date, 1000 as size_sqft FROM ura_transactions WHERE 1=1"
            params = []
            if project:
                query += " AND project LIKE ?"
                params.append(f"%{project}%")
            query += f" ORDER BY transaction_date DESC LIMIT {limit}"
            df = pd.read_sql_query(query, conn, params=params)
        else:
            # Fallback to HDB transactions for benchmarking
            # We combine Block + Street Name + Town to show a more descriptive "Project/Location"
            query = f"""
                SELECT (block || ' ' || street_name || ' (' || town || ')') as project, 
                       resale_price as price, 
                       'N/A' as profit, 
                       month as date,
                       (floor_area_sqm * 10.7639) as size_sqft,
                       town
                FROM hdb_transactions 
                WHERE 1=1
            """
            params = []
            if project:
                query += " AND (street_name LIKE ? OR town LIKE ? OR project LIKE ?)"
                params.extend([f"%{project}%", f"%{project}%", f"%{project}%"])
            else:
                query += " AND month = (SELECT MAX(month) FROM hdb_transactions)"

            query += f" ORDER BY resale_price DESC LIMIT {limit}"
            df = pd.read_sql_query(query, conn, params=params)

        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


@app.get("/api/launches-live")
def get_launches_live():
    conn = get_db_connection()
    try:
        # 1. Get manually populated benchamark data (high accuracy for top projects)
        bench_df = pd.read_sql_query(
            "SELECT * FROM new_launches ORDER BY year DESC", conn
        )

        # 2. Try to supplement with real private transactions (New Sale) if table exists
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='private_transactions'"
        )
        if cursor.fetchone():
            # Add dynamic logic here if needed
            pass

        return bench_df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


# ── LIVE MACRO DATA RETRIEVAL (WEEKLY AUTOMATED CACHE) ────────────────────────
CACHE_FILE_LIVE = os.path.join(base_dir, "data", "macro_live_cache.json")


def _parse_quarter(q_str):
    m = re.search(r"(\d{2,4})[-_\s]?[Qq](\d)", str(q_str))
    if m:
        year = int(m.group(1))
        if year < 100:
            year += 2000
        return year, int(m.group(2))
    return (0, 0)


def _q_label(year, q):
    return f"{str(year)[2:]}Q{q}"


def _forecast_series(series_data, key_fields, num_periods=2, is_year=False):
    if len(series_data) < 4:
        return []
    predictions = []
    last_item = series_data[-1]
    if is_year:
        last_yr = int(last_item.get("year") or 2025)
        for step in range(1, num_periods + 1):
            pred_yr = str(last_yr + step)
            pred_dict = {"year": pred_yr, "is_forecast": True}
            for kf in key_fields:
                y = [float(x.get(kf) or 0.0) for x in series_data]
                n = len(y)
                x = list(range(n))
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xx = sum(i * i for i in x)
                sum_xy = sum(x[i] * y[i] for i in range(n))
                denom = n * sum_xx - sum_x * sum_x
                m = (n * sum_xy - sum_x * sum_y) / denom if denom != 0 else 0
                c = (sum_y * sum_xx - sum_x * sum_xy) / denom if denom != 0 else y[-1]
                pred_val = m * (n - 1 + step) + c
                pred_dict[kf] = max(0.1, round(pred_val, 1))
            predictions.append(pred_dict)
    else:
        last_q = last_item.get("q")
        yr, q_num = _parse_quarter(last_q)
        if yr == 0:
            yr = 2026
            q_num = 1
        for step in range(1, num_periods + 1):
            q_num += 1
            if q_num > 4:
                q_num = 1
                yr += 1
            pred_q = _q_label(yr, q_num)
            pred_dict = {"q": pred_q, "is_forecast": True}
            for kf in key_fields:
                y = [float(x.get(kf) or 0.0) for x in series_data]
                n = len(y)
                x = list(range(n))
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xx = sum(i * i for i in x)
                sum_xy = sum(x[i] * y[i] for i in range(n))
                denom = n * sum_xx - sum_x * sum_x
                m = (n * sum_xy - sum_x * sum_y) / denom if denom != 0 else 0
                c = (sum_y * sum_xx - sum_x * sum_xy) / denom if denom != 0 else y[-1]
                pred_val = m * (n - 1 + step) + c
                pred_dict[kf] = max(0.1, round(pred_val, 1))
            predictions.append(pred_dict)
    return predictions


def fetch_json_live(url, label=""):
    try:
        ctx = ssl.create_default_context()
        headers = {
            "User-Agent": "SGPropertyDashboard/2.0 (open-source; data.gov.sg public API)",
            "Accept": "application/json",
        }
        api_key = os.getenv("DATA_GOV_API_KEY")
        if api_key:
            headers["api-key"] = api_key
            headers["x-api-key"] = api_key
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [Warning] Could not fetch {label or url[:60]}: {e}")
        return None


def datagov_live(dataset_id, limit=40, sort="quarter desc"):
    import urllib.parse

    url = (
        f"https://data.gov.sg/api/action/datastore_search"
        f"?resource_id={dataset_id}&limit={limit}&sort={urllib.parse.quote(sort)}"
    )
    d = fetch_json_live(url, label=f"data.gov.sg/{dataset_id[:12]}...")
    if d and d.get("success") and d["result"].get("records"):
        return d["result"]["records"]
    return None


def fetch_ppi_live():
    recs = datagov_live("d_f65e490a8ad430f60a9a3d9df2bff2a0", limit=300)
    if not recs:
        return []
    quarters = {}
    for r in recs:
        q = r.get("quarter")
        if not q:
            continue
        segment = r.get("market_segment")
        val = float(r.get("price_index") or 0)
        if q not in quarters:
            quarters[q] = {"ccr": 0.0, "rcr": 0.0, "ocr": 0.0}
        if segment == "Core Central Region":
            quarters[q]["ccr"] = val
        elif segment == "Rest of Central Region":
            quarters[q]["rcr"] = val
        elif segment == "Outside Central Region":
            quarters[q]["ocr"] = val
    sorted_qs = sorted(quarters.keys(), key=_parse_quarter)
    result = []
    for q in sorted_qs[-10:]:
        yr, q_num = _parse_quarter(q)
        result.append(
            {
                "q": _q_label(yr, q_num),
                "ccr": quarters[q]["ccr"],
                "rcr": quarters[q]["rcr"],
                "ocr": quarters[q]["ocr"],
            }
        )
    return result


def fetch_unsold_live():
    recs = datagov_live("d_84d05d45049108f0fd2e99b66bd19cfe", limit=1000)
    if not recs:
        return []
    quarters = {}
    for r in recs:
        q = r.get("quarter")
        if not q:
            continue
        units = int(r.get("units") or 0)
        if q not in quarters:
            quarters[q] = 0
        quarters[q] += units
    sorted_qs = sorted(quarters.keys(), key=_parse_quarter)
    result = []
    for q in sorted_qs[-10:]:
        yr, q_num = _parse_quarter(q)
        result.append({"q": _q_label(yr, q_num), "unsold": quarters[q]})
    return result


def fetch_launches_live():
    DATASETS = {
        "ccr": "d_c287c8be114bfa7d055b27ab2c87de83",
        "rcr": "d_5785799d63a9da091f4e0b456291eeb8",
        "ocr": "d_1a7823f3d31e7db4b426833833762bab",
    }
    merged = {}
    for region, rid in DATASETS.items():
        recs = datagov_live(rid, limit=500)
        if not recs:
            continue
        quarter_sums = {}
        for r in recs:
            q = r.get("quarter")
            if not q:
                continue
            type_of_sale = r.get("type_of_sale")
            units = int(r.get("units") or 0)
            if type_of_sale != "New Sale":
                continue
            if q not in quarter_sums:
                quarter_sums[q] = 0
            quarter_sums[q] += units
        for q, val in quarter_sums.items():
            yr, q_num = _parse_quarter(q)
            label = _q_label(yr, q_num)
            if label not in merged:
                merged[label] = {"q": label, "ccr": 0, "rcr": 0, "ocr": 0}
            merged[label][region] = val
    if not merged:
        return []
    rows = sorted(merged.values(), key=lambda r: _parse_quarter(r["q"]))
    return rows[-10:]


def fetch_gdp_live():
    res = datagov_live("d_579806298539b7ea57b855655b3d63b2", limit=20)
    gdp_rows = []
    if res:
        for r in res:
            try:
                gdp_rows.append(
                    {
                        "year": int(r.get("year") or 0),
                        "gdp": float(r.get("gdp") or r.get("value") or 0),
                    }
                )
            except:
                pass
    if not gdp_rows:
        gdp_rows = [
            {"year": 2018, "gdp": 3.5},
            {"year": 2019, "gdp": 1.1},
            {"year": 2020, "gdp": -3.9},
            {"year": 2021, "gdp": 8.9},
            {"year": 2022, "gdp": 3.6},
            {"year": 2023, "gdp": 1.1},
            {"year": 2024, "gdp": 5.3},
            {"year": 2025, "gdp": 5.0},
        ]
    gdp_rows.sort(key=lambda x: x["year"])
    return gdp_rows[-8:]


def fetch_unemployment_live():
    res = datagov_live(
        "d_a1d4e3e9c7ea07c082729a674313f890", limit=20, sort="quarter desc"
    )
    rows = []
    if res:
        for r in res:
            try:
                yr, q_num = _parse_quarter(r.get("quarter"))
                val = float(r.get("unemployment_rate") or r.get("value") or 0)
                rows.append({"q": _q_label(yr, q_num), "rate": val})
            except:
                pass
    if not rows:
        rows = [
            {"q": "24Q1", "rate": 1.9},
            {"q": "24Q3", "rate": 2.0},
            {"q": "25Q1", "rate": 2.1},
            {"q": "25Q3", "rate": 2.0},
            {"q": "26Q1", "rate": 2.1},
        ]
    rows.sort(key=lambda x: _parse_quarter(x["q"]))
    return rows[-8:]


def fetch_hdb_live():
    recs = datagov_live("d_14f63e595975691e7c24a27ae4c07c79", limit=200)
    if not recs:
        return []
    sorted_qs = sorted(recs, key=lambda x: _parse_quarter(x.get("quarter")))
    result = []
    for r in sorted_qs[-10:]:
        yr, q_num = _parse_quarter(r.get("quarter"))
        result.append({"q": _q_label(yr, q_num), "index": float(r.get("index") or 0.0)})
    return result


def fetch_pipeline_live():
    recs = datagov_live("d_84d05d45049108f0fd2e99b66bd19cfe", limit=1000)
    if not recs:
        return {}
    qs = [r.get("quarter") for r in recs if r.get("quarter")]
    if not qs:
        return {}
    latest_q = max(qs, key=_parse_quarter)
    latest_recs = [r for r in recs if r.get("quarter") == latest_q]
    pipeline_data = {
        "ccr": {"immediate": 0, "medium": 0},
        "rcr": {"immediate": 0, "medium": 0},
        "ocr": {"immediate": 0, "medium": 0},
        "quarter": latest_q,
    }
    segment_map = {
        "Core Central Region": "ccr",
        "Rest of Central Region": "rcr",
        "Outside Central Region": "ocr",
    }
    for r in latest_recs:
        seg = segment_map.get(r.get("market_segment"))
        if not seg:
            continue
        comp = r.get("completion_status")
        launch = r.get("launch_status")
        pre_req = r.get("pre_requisites_status")
        units = int(r.get("units") or 0)

        if comp == "Uncompleted":
            if launch == "Not Launch Yet" and pre_req == "With Pre-Requisites":
                pipeline_data[seg]["immediate"] += units
            elif launch == "na" and pre_req == "Without Pre-Requisites":
                pipeline_data[seg]["medium"] += units
    return pipeline_data


@app.get("/api/macro-live")
def get_macro_live(refresh: bool = Query(False)):
    now = datetime.datetime.now()
    need_refresh = True
    cache_data = {}

    os.makedirs(os.path.dirname(CACHE_FILE_LIVE), exist_ok=True)
    if os.path.exists(CACHE_FILE_LIVE) and not refresh:
        try:
            with open(CACHE_FILE_LIVE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            next_dt = datetime.datetime.strptime(
                cache_data.get("next_retrieve_date", ""), "%Y-%m-%d %H:%M:%S"
            )
            if now < next_dt:
                need_refresh = False
        except Exception as e:
            print(f"Error loading live cache: {e}")
            need_refresh = True

    if need_refresh:
        print(
            "[Sync] Live Cache expired or missing. Fetching fresh weekly data from Gov APIs..."
        )
        try:
            ppi_data = fetch_ppi_live()
            unsold_data = fetch_unsold_live()
            launches_data = fetch_launches_live()
            gdp_data = fetch_gdp_live()
            unemployment_data = fetch_unemployment_live()
            hdb_data = fetch_hdb_live()
            pipeline_data = fetch_pipeline_live()

            # Compute 2-quarter forecasts using linear trend regression
            ppi_forecast = _forecast_series(
                ppi_data, ["ccr", "rcr", "ocr"], num_periods=2
            )
            unsold_forecast = _forecast_series(unsold_data, ["unsold"], num_periods=2)
            launches_forecast = _forecast_series(
                launches_data, ["ccr", "rcr", "ocr"], num_periods=2
            )
            gdp_forecast = _forecast_series(
                gdp_data, ["gdp"], num_periods=1, is_year=True
            )
            unemployment_forecast = _forecast_series(
                unemployment_data, ["rate"], num_periods=2
            )
            hdb_forecast = _forecast_series(hdb_data, ["index"], num_periods=2)

            payload = {
                "ppi": ppi_data,
                "ppi_forecast": ppi_forecast,
                "unsold": unsold_data,
                "unsold_forecast": unsold_forecast,
                "launches": launches_data,
                "launches_forecast": launches_forecast,
                "gdp": gdp_data,
                "gdp_forecast": gdp_forecast,
                "unemployment": unemployment_data,
                "unemployment_forecast": unemployment_forecast,
                "hdb": hdb_data,
                "hdb_forecast": hdb_forecast,
                "pipeline": pipeline_data,
            }

            last_date_str = now.strftime("%Y-%m-%d %H:%M:%S")
            next_date_str = (now + datetime.timedelta(days=7)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            cache_data = {
                "last_retrieve_date": last_date_str,
                "next_retrieve_date": next_date_str,
                "data": payload,
            }

            with open(CACHE_FILE_LIVE, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error during live fetch: {e}")
            if cache_data:
                cache_data["next_retrieve_date"] = (
                    now + datetime.timedelta(hours=1)
                ).strftime("%Y-%m-%d %H:%M:%S")
            else:
                return {"error": f"Failed to fetch data and no cached data: {e}"}

    return cache_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
