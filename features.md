# Property Analytics Dashboard — High-Level Requirements

## Project Overview

Build a bilingual (**English + 中文**) property intelligence dashboard using:

* Python (data pipeline / ETL)
* SQLite (data storage)
* FastAPI (API layer)
* Frontend dashboard (Next.js / React)
* ECharts / Recharts (visualizations)
* Scheduled data refresh (monthly minimum, optional daily refresh)

## Primary Data Sources

### Government Sources

* Singapore Data.gov.sg
* HDB resale datasets
* URA transaction datasets
* GLS land sales datasets
* Government policy announcements

## Functional Requirements

---

# 1. Market Performance & Price Trends

## 1.1 HDB Resale Price Index — Annual Average Growth Rates

### Requirement

Display annual average growth rates across different historical periods.

### Output

* Line chart
* CAGR comparison
* Year-period breakdown

---

## 1.2 HDB Resale Price Index — Quarterly Performance (QoQ)

### Requirement

Track quarterly movements and identify early moderation signals.

### Output

* Quarterly trend line
* QoQ growth chart
* Highlight slowdown periods

---

## 1.3 Historical Annual Percentage Change Table

### Requirement

Provide annual performance table for long-term comparison.

### Output

* Data table
* YoY percentage changes

---

## 1.4 Unsold Private Residential Inventory

### Requirement

Track quarterly inventory levels by region.

### Breakdown

* CCR
* RCR
* OCR

### Output

* Stacked bar chart
* Trend analysis

---

# 2. Land Cost & Bidding Intelligence

## 2.1 Historical Land Cost Timeline

### Requirement

Track average land cost growth over time.

### Output

* Timeline chart
* Average psf ppr trend

---

## 2.2 GLS Average Land Price vs Bidding Activity

### Requirement

Compare land pricing with bidding competitiveness.

### Output

* Dual-axis chart
* Land price trend
* Average bids per site

---

## 2.3 Regional Land Price Analysis (CCR)

### Requirement

Compare:

* Enbloc sites
* GLS sites

### Time Period

2019–2026

### Output

* Comparative trend chart

---

## 2.4 Regional Land Price Analysis (OCR)

### Requirement

Track GLS land price evolution.

### Time Period

2019–2026

### Output

* Historical trend chart

---

## 2.5 Upcoming GLS Land Prices by Region

### Requirement

Compare latest land prices across regions.

### Output

* Bar chart
* OCR vs RCR vs CCR comparison

---

## 2.6 Land Tender Comparison

### Requirement

Compare historical vs current bid prices.

### Example

* Dunearn Road case study

### Output

* Comparative analysis chart

---

# 3. Investment Strategy & Predictive Models

## 3.1 Property Capital Building Journey

### Requirement

Visualize property upgrading journey.

### Stages

* HDB BTO
* Resale HDB
* Private Property
* Higher Value Property

### Output

* Timeline diagram

---

## 3.2 Estimated Returns Model

### Requirement

Calculate investment returns.

### Include

* Initial cash outlay
* Mortgage costs
* Selling proceeds
* Net returns

### Output

* Financial model dashboard

---

## 3.3 Land Price to Selling Price Correlation

### Requirement

Predict launch price using land acquisition cost.

### Output

* Correlation chart
* Predictive model

---

## 3.4 Capital Certainty Model

### Requirement

Compare:

* Higher quantum purchases
* Potential capital appreciation

### Output

* Scenario model

---

## 3.5 Portfolio Diversification Analysis

### Requirement

Compare:

* Singapore property
* International property

### Output

* Comparison matrix

---

# 4. Policy & Regulatory Analytics

## 4.1 EC Policy Framework Changes

### Requirement

Track policy changes.

### Areas

* MOP
* Quota
* Priority period
* Payment scheme

### Output

* Four-quadrant framework chart

---

## 4.2 EC MOP Timeline

### Requirement

Compare:

* Before May 2026
* After May 2026

### Output

* Timeline chart

---

## 4.3 First-Timer Priority Quota Shift

### Requirement

Track quota allocation changes.

### Output

* Historical comparison chart

---

## 4.4 Priority Period Extension

### Requirement

Compare:

* 1 month
* 2 years

### Output

* Comparison chart

---

## 4.5 Payment Scheme Comparison

### Requirement

Compare:

* Deferred Payment Scheme (DPS)
* Normal Payment Scheme (NPS)

### Output

* Side-by-side comparison table

---

# 5. Benchmark Performance Tables

## 5.1 Top 20 Most Profitable EC Resale Transactions

### Requirement

Rank highest profit transactions.

### Output

* Ranked table
* Gross profit metrics

---

## 5.2 Upcoming EC Launch Pipeline

### Requirement

Compare:

* Land acquisition price
* Estimated launch price

### Output

* Bar chart

---

# Non-Functional Requirements

## Data Refresh

* Monthly automatic refresh (minimum)
* Optional daily refresh

## Language Support

* English
* Simplified Chinese

## User Features

* Filter by region
* Filter by property type
* Filter by timeframe
* Export charts/images

## Performance

* Fast dashboard loading
* Mobile responsive

## Future Scalability

* Upgrade SQLite → PostgreSQL if traffic increases
* Add AI forecasting modules
* Add user login system

---

# Success Metrics

* Automated reporting
* Faster market research
* Better investment decision support
* Strong visual storytelling for property clients/investors
