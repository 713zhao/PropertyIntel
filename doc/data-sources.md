# PropIntel Data Sources & Methodology

This document outlines the data sources and calculation logic for every diagram and table across the PropIntel dashboard.

## 1. Dashboard (首页)

| Diagram / Stat | Data Source | Dataset ID / Table |
| :--- | :--- | :--- |
| **Public vs Private Index** | data.gov.sg | `hdb_resale_index` (d_14f63e595975691e7c24a27ae4c07c79) & `private_property_index` (d_97f8a2e995022d311c6c68cfda6d034c) |
| **Avg Price Growth** | data.gov.sg | Calculated YoY from `hdb_resale_index` |
| **Total Inventory** | Mock Data | `unsoldInventory` in `mockData.ts` (Proxy for market supply) |
| **Avg Land Cost** | Benchmark Data | `gls_residential` table (Aggregated from 2024–2025 GLS results) |

---

## 2. Market Trends (市场趋势)

| Diagram / Stat | Data Source | Details |
| :--- | :--- | :--- |
| **Market Price Gap** | data.gov.sg | Ratio calculation: `Private Property Index / HDB Resale Index`. Indicates "upgrade" affordability. |
| **Affordability Index** | data.gov.sg + SingStat | Ratio calculation: `Median Household Income / Private Property Index`. Higher value = Better affordability. |
| **Median Household Income** | data.gov.sg / SingStat | `household_income` table. 2017–2023 from d_37ff979fd327acc0df0f412a29ea352f. 2024 ($11,544) and 2025 ($12,185) from SingStat. |
| **Population Growth** | data.gov.sg | `population_indicators` table (d_3d227e5d9fdec73f3bcadce671c333a6). Proxy for residential demand. |

---

## 3. Land Intelligence (土地情报)

| Diagram / Stat | Data Source | Details |
| :--- | :--- | :--- |
| **Historical Land Cost** | URA / GLS | `gls_residential` table. Aggregated awarded price ($ psf ppr) for CCR, RCR, and OCR regions (2018–2026). |
| **Land vs. Launch Price** | URA / New Launches | Correlation between site acquisition cost and final project launch price (e.g., Lentoria, Watten House). |
| **New Launch Benchmarks** | Market Reports | Manually curated table of 2024–2026 launches based on latest transaction benchmarks. |

---

## 4. Policy Benchmarks (政策基准)

| Diagram / Stat | Data Source | Details |
| :--- | :--- | :--- |
| **Recent Resale Transactions**| data.gov.sg | `hdb_transactions` table (d_8b84c4ee58e3cfc0ece0d773c8ca6abc). Fetches latest 100k registration records. |
| **Project Names** | data.gov.sg | Derived by combining `Block` + `Street Name` + `Town` from the HDB dataset. |

---

## 5. Investment Strategy (财务建模)

| Section | Logic / Source | Methodology |
| :--- | :--- | :--- |
| **Acquisition Cost** | Policy Rates | **BSD**: Calculated using 2024 IRAS tiers. **ABSD**: Dynamic rates based on user status (0% for SC 1st, 20% for SC 2nd, 60% for Foreigners). |
| **Total Cash Needed** | Policy Logic | `(Price x Downpayment%) + BSD + ABSD + Legal Fees`. Minimum downpayment capped at 25% (MAS LTV limit). |
| **Mortgage Stress Test** | Financial Formula | Amortization formula at 3.5% (current) and 5.5% (stress). Req. Income based on **55% TDSR proxy**. |
| **Net Yield** | IRA / Market | **Gross Rent - Property Tax - Maintenance**. Property Tax uses 2024 progressive rates for Non-Owner Occupied properties (AV = 85% of rent). |
| **Cash-on-Cash** | Leveraged Return | `(Annual Net Cashflow / Total Initial Cash Outlay)`. Updated in real-time based on interest rate slider. |
| **Amenities Engine** | Heuristic Mapping | Intelligence engine that maps town names (e.g., "BISHAN") to specific nearby Primary Schools (1km), Malls, and MRT stations. |

---

## Data Pipeline Scripts

- `fetch_data_gov.py`: Primary script for fetching macro indices and population data.
- `fetch_hdb_live.py`: High-performance streaming script for processing large-scale transaction datasets.
- `populate_land_data.py`: Aggregator for land sales and launch benchmarks.
