# 🚕 Urban Mobility Intelligence

> **A production-style business intelligence and analytics platform for understanding NYC taxi demand, weather sensitivity, spatial demand, revenue behavior, and operational patterns.**

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![Google BigQuery](https://img.shields.io/badge/Google%20BigQuery-Analytics%20Warehouse-4285F4?logo=googlecloud)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Visualization-3F4F75)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 📌 Project Overview

Urban Mobility Intelligence is an end-to-end analytics project built around **2021 NYC Green Taxi trip data** and daily weather observations.

The project is designed to demonstrate how a data professional can move from raw analytical requirements to a reusable analytical warehouse, statistical analysis, business intelligence questions, and an interactive executive dashboard.

Rather than presenting a collection of disconnected charts, the application is structured as a small **urban mobility intelligence platform**.

The platform answers questions such as:

- How much taxi demand occurred during 2021?
- Which months generated the highest and lowest demand?
- What hours of the day experience the greatest activity?
- Which weekdays are strongest?
- Which pickup zones generate the greatest demand?
- How does precipitation affect taxi demand?
- How does snowfall affect demand?
- Does temperature have a meaningful relationship with demand?
- Which weather conditions produce the strongest revenue performance?
- How does weather affect average daily gross customer charges?
- Which operational periods deserve the most attention?
- What can be confidently concluded from the available data?
- Which business questions require additional datasets before they can be answered?

The guiding principle is simple:

> **Do not manufacture an answer when the underlying data cannot support it.**

That principle is reflected throughout the analytical architecture and the Business Intelligence Questions page.

---

# 🎯 Project Goals

The project was built to demonstrate practical capability across several areas of modern data analytics:

1. Data ingestion
2. Cloud data warehousing
3. SQL-based analytical modeling
4. Python analytics
5. Statistical analysis
6. Data validation
7. Business intelligence
8. Interactive visualization
9. Dashboard architecture
10. Analytical interpretation
11. Reproducible workflows
12. Portfolio-quality engineering practices

The project intentionally combines **data engineering, analytics engineering, statistical analysis, and business intelligence** rather than treating them as isolated disciplines.

---

# 🧠 Analytical Philosophy

A strong dashboard is not simply a collection of attractive visualizations.

The platform separates three levels of analytical reasoning.

### 1. Observed Facts

These are values directly calculated from the analytical datasets.

Examples:

- Total trips
- Average daily trips
- Monthly trips
- Hourly trips
- Pickup-zone trips
- Daily revenue
- Daily tips
- Weather observations

### 2. Analytical Interpretation

These are conclusions derived from statistical relationships and comparisons.

Examples:

- Snowfall has a stronger negative relationship with demand than temperature.
- Rainy days produce fewer average daily trips than dry days.
- Weather categories exhibit statistically different demand distributions.

### 3. Future Capabilities

These are questions that require datasets not currently present in the warehouse.

Examples:

- Real-time vehicle positions
- Driver availability
- Transit telemetry
- Traffic congestion
- EV telemetry
- Ride-hailing competitor data
- Weather radar
- Live fleet status

Keeping these categories separate makes the dashboard more credible and prevents unsupported business claims.

---

# 🏗️ Architecture

The platform follows a layered architecture designed to separate data access, analytics, visualization, and business interpretation.

```text
                    ┌──────────────────────────────┐
                    │        NYC Taxi Data         │
                    │      2021 Green Taxi         │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │      BigQuery Raw Layer      │
                    │        mobility_raw          │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    │                              │
                    ▼                              ▼
          ┌───────────────────┐          ┌───────────────────┐
          │ Open-Meteo Weather│          │ Analytical SQL    │
          │      Ingestion    │          │   Transformations │
          └─────────┬─────────┘          └─────────┬─────────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │    BigQuery Analytics Layer │
                    │     mobility_analytics      │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │ Data Loader │      │   Metrics   │      │ Statistical │
       │             │      │   Engine    │      │   Analysis  │
       └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │  Visualization Layer│
                         │       Plotly        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Streamlit App    │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
      │   Executive   │      │    Weather    │      │      BI       │
      │   Dashboard   │      │   Geography   │      │   Questions   │
      └───────────────┘      └───────────────┘      └───────────────┘
```

---

# 🧱 Four-Layer Intelligence Model

The dashboard is conceptually organized around four analytical layers.

## Layer 1 — Executive Pulse

The executive layer provides the highest-level operational picture.

It focuses on metrics such as:

- Total annual trips
- Average daily trips
- Average daily gross customer charges
- Average daily tips
- Monthly demand
- Hourly demand
- Weekday demand

The purpose is to allow a decision-maker to understand the overall mobility environment before entering deeper analysis.

---

## Layer 2 — Correlative Engine

This layer investigates relationships between weather and taxi demand.

Variables include:

- Temperature
- Precipitation
- Snowfall
- Wind
- Weather category
- Daily trips
- Revenue
- Tips
- Average charge per trip

The platform does not treat correlation as causation. Statistical relationships are presented as evidence rather than automatic causal explanations.

---

## Layer 3 — Spatial Ground Truth

This layer examines where demand occurs.

The primary spatial analytical unit is the **pickup zone**.

The dashboard uses pickup-zone summaries to identify:

- Highest-demand zones
- Lowest-demand zones
- Concentration of demand
- Geographic differences in activity

This provides a spatial perspective that complements the temporal and weather analyses.

---

## Layer 4 — Scenario and Strategic Intelligence

The platform uses the available evidence to support business questions and operational interpretation.

The BI layer focuses on questions that can actually be answered from the warehouse.

Questions requiring unavailable data are intentionally excluded rather than estimated without evidence.

---

# ☁️ Google BigQuery Architecture

The project uses Google BigQuery as the analytical warehouse.

The architecture separates raw external data from analytical summaries.

## Raw Dataset

```text
mobility_raw
```

Current weather table:

```text
daily_weather_2021
```

This table contains daily NYC weather observations used for weather-demand and weather-revenue analysis.

## Analytics Dataset

```text
mobility_analytics
```

The analytical warehouse contains summary tables designed specifically for dashboard queries.

This is important because the Streamlit application should not repeatedly scan the entire underlying trip dataset for every chart.

Instead, the expensive analytical work is performed upstream and the application reads compact analytical summaries.

---

# 📊 BigQuery Analytical Tables

The project uses the following analytical tables.

### `monthly_trip_summary_2021`

Monthly demand summary for 2021.

Used for:

- Monthly trend analysis
- Seasonality analysis
- Executive dashboard reporting

### `hourly_trip_summary_2021`

Hourly demand summary.

Used for:

- Demand concentration
- Peak-hour identification
- Operational intelligence

### `weekday_trip_summary_2021`

Weekday demand summary.

Used for:

- Weekday comparisons
- Operational planning
- Weekly demand patterns

### `pickup_zone_summary_2021`

Pickup-zone demand summary.

Used for:

- Spatial demand analysis
- Geographic ranking
- Demand concentration

### `precipitation_impact_2021`

Precipitation impact summary.

Used for:

- Rainfall analysis
- Demand comparisons
- Weather sensitivity

### `snowfall_impact_2021`

Snowfall impact summary.

Used for:

- Snow-day demand analysis
- Weather severity comparisons

### `temperature_impact_2021`

Temperature impact summary.

Used for:

- Temperature-demand relationships
- Regression analysis

### `wind_impact_2021`

Wind impact summary.

Used for:

- Wind-demand relationships

### `weather_impact_summary_2021`

Overall weather category impact summary.

Used for:

- Dry vs precipitation vs snow comparisons
- Executive weather intelligence

### `weather_demand_daily_2021`

Daily weather and taxi demand dataset.

Used for:

- Correlation analysis
- Regression
- Multivariate modeling

### `taxi_revenue_weather_daily_2021`

Daily taxi revenue and weather observations.

Used for:

- Revenue-weather analysis
- Daily gross charge analysis
- Tips analysis

### `taxi_revenue_weather_impact_2021`

Aggregated revenue impact by weather condition.

Used for:

- Revenue comparison
- Weather-sensitive financial intelligence

### `weekday_weather_impact_2021`

Weather-demand relationships segmented by weekday.

Used for:

- Weather × weekday analysis
- Operational interpretation

---

# 🌦️ Weather Data Ingestion

Weather data is collected through the `ingest_weather.py` pipeline.

The ingestion process retrieves daily NYC weather observations from Open-Meteo for 2021.

Conceptually:

```text
Open-Meteo API
      │
      ▼
Python ingestion script
      │
      ▼
Daily weather dataframe
      │
      ▼
BigQuery
      │
      ▼
mobility_raw.daily_weather_2021
```

The ingestion process creates a reproducible bridge between an external API and the analytical warehouse.

This demonstrates an important real-world analytics pattern:

> **External operational data → ingestion → cloud warehouse → analytical model → BI application**

---

# 🐍 Python Application Structure

The repository intentionally separates responsibilities across modules.

```text
urban-mobility-analytics/
│
├── app.py
├── bigquery.py
├── charts.py
├── data_loader.py
├── ingest_weather.py
├── metrics.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── analysis/
│   ├── statistical_analysis.py
│   └── outputs/
│
└── pages/
    ├── 1_Executive_Dashboard.py
    ├── 2_Weather_Geography.py
    └── 3_BI_Questions.py
```

---

# 📁 Module Responsibilities

## `app.py`

The main Streamlit application entry point.

Responsibilities include:

- Application configuration
- Executive-level presentation
- Global dashboard structure
- Main command-center experience
- Analytical interpretation section
- Application footer

The app is intentionally kept separate from the underlying data-access and chart-generation modules.

---

## `bigquery.py`

Centralized BigQuery access layer.

Responsibilities include:

- Creating the BigQuery client
- Loading analytical tables
- Keeping database access logic out of dashboard pages

This separation makes the application easier to maintain and test.

---

## `data_loader.py`

The application data-loading layer.

It provides reusable cached functions for analytical datasets.

Examples include:

```text
load_monthly_trips()
load_hourly_trips()
load_weekday_trips()
load_pickup_zones()
load_daily_weather()
load_weather_impact()
load_temperature_impact()
load_precipitation_impact()
load_snowfall_impact()
load_wind_impact()
load_weekday_weather_impact()
load_revenue_weather_impact()
```

Caching reduces unnecessary repeated BigQuery requests during Streamlit reruns.

---

## `metrics.py`

Contains reusable analytical calculations and metric logic.

The objective is to prevent important business calculations from being duplicated throughout UI code.

This improves consistency between dashboard components.

---

## `charts.py`

Centralized Plotly visualization layer.

The module contains chart-generation functions for:

- Monthly trips
- Hourly trips
- Weekday trips
- Pickup zones
- Weather demand
- Temperature demand
- Weather revenue
- Temperature impact
- Precipitation impact
- Snowfall impact
- Wind impact
- Weekday weather relationships

The separation means the Streamlit pages can focus on the analytical story rather than low-level chart construction.

---

## `ingest_weather.py`

External weather API ingestion pipeline.

Responsibilities include:

- Requesting daily weather observations
- Building the weather dataset
- Loading the dataset into BigQuery
- Replacing the target 2021 weather table

---

# 📈 Statistical Analysis

The repository contains a dedicated statistical analysis pipeline:

```text
analysis/statistical_analysis.py
```

This script validates the analytical datasets and performs statistical analysis before results are exposed through the dashboard.

The analysis includes:

- Dataset validation
- Pearson correlations
- Simple linear regressions
- Multivariate regression
- Regression diagnostics
- Weather-category comparisons
- ANOVA
- Tukey post-hoc comparisons
- Effect-size calculations
- Variance inflation factor analysis
- Demand concentration analysis
- Revenue-weather analysis
- Confidence intervals

---

# 🔬 Statistical Findings

The 2021 analysis produced several important findings.

## Dataset Scale

The analytical validation covered:

| Dataset | Rows | Columns |
|---|---:|---:|
| Monthly trips | 12 | 3 |
| Hourly trips | 24 | 3 |
| Weekday trips | 7 | 4 |
| Pickup zones | 257 | 4 |
| Daily weather | 365 | 10 |
| Weather impact | 4 | 7 |
| Revenue/weather | 365 | 10 |

---

# 🚕 Core Demand Metrics

The 2021 dataset contains approximately:

**1,016,954 taxi trips**.

Average daily demand was approximately:

**2,786 trips per day**.

Average daily gross customer charges were approximately:

**$64,264.93 per day**.

Average daily tips were approximately:

**$3,079.88 per day**.

These values provide the baseline against which weather and operational differences can be evaluated.

---

# 🌧️ Weather Intelligence

Weather is one of the major analytical dimensions in the project.

The platform groups observations into categories such as:

- Dry
- Light precipitation
- Rain
- Snow

This allows decision-makers to compare operational performance under different environmental conditions.

---

# 📊 Weather Category Results

Approximate average daily demand:

| Weather condition | Average daily trips |
|---|---:|
| Dry | 2,849 |
| Light precipitation | 2,855 |
| Rain | 2,740 |
| Snow | 2,252 |

The snow category has the lowest average demand in the observed data.

The comparison demonstrates why simply treating all precipitation as one category can hide meaningful operational differences.

---

# 💰 Weather and Revenue

Average daily gross customer charges were approximately:

| Weather condition | Avg. daily gross charges |
|---|---:|
| Dry | $68,931.46 |
| Light precipitation | $68,923.36 |
| Rain | $65,942.37 |
|

Rainy conditions generated approximately **$2,989 less average daily gross customer charges than dry conditions**, equivalent to roughly **4.34% lower daily gross charges**.

Average daily tips were approximately:

- Dry: $3,336.30
- Rain: $3,253.89

The observed difference was approximately **$82.41 per day**.

Average charge per trip was approximately:

- Dry: $24.17
- Rain: $24.05

These numbers are descriptive comparisons and should not automatically be interpreted as causal effects.

---

# 📐 Correlation Analysis

Pearson correlation analysis produced the following relationships with daily taxi demand.

| Variable | Pearson r | Interpretation |
|---|---:|---|
| Average temperature | 0.1199 | Weak positive relationship |
| Precipitation | -0.1332 | Weak negative relationship |
| Snowfall | -0.2834 | Stronger negative relationship than rain/temperature |
| Maximum wind speed | -0.0375 | Very weak relationship |

The most notable relationship is snowfall and demand.

The snowfall correlation is approximately:

```text
r = -0.2834
```

This indicates a negative relationship, although correlation alone does not establish causality.

---

# 📉 Regression Analysis

Simple regressions were also evaluated.

### Temperature

```text
Coefficient ≈ 4.5841
R² ≈ 0.0144
p ≈ 0.0220
```

### Precipitation

```text
Coefficient ≈ -212.8563
R² ≈ 0.0177
p ≈ 0.0109
```

### Snowfall

```text
Coefficient ≈ -293.5389
R² ≈ 0.0803
```

The low R² values are important.

They indicate that weather variables alone explain only a relatively small portion of daily demand variation.

This is an important analytical finding because it prevents overclaiming the importance of weather.

---

# 🧮 Multivariate Regression

A multivariate regression combined:

- Average temperature
- Precipitation
- Snowfall
- Maximum wind speed

The model produced approximately:

```text
R² = 0.0960
Adjusted R² = 0.0859
```

The overall model was statistically significant.

However, the model still explains less than 10% of daily demand variation.

This strongly suggests that demand is influenced by many additional factors beyond the weather variables currently available.

Potential missing explanatory variables include:

- Holidays
- Events
- Tourism
- Economic activity
- Transit disruptions
- Traffic congestion
- Service availability
- Fleet size
- Fuel prices
- Airport activity
- Major disruptions
- Seasonal behavioral changes

---

# 🧪 ANOVA

Weather-category differences were also evaluated using ANOVA.

Observed result:

```text
F-statistic ≈ 6.9232
p-value ≈ 0.000153
```

The result provides evidence that average daily demand differs across the observed weather categories.

Post-hoc comparisons are included in the generated analytical outputs so that category-level differences can be investigated beyond the overall ANOVA result.

---

# 📊 Why Statistical Testing Matters

A dashboard can visually suggest that one category performs differently from another.

Statistical testing adds another layer of evidence.

The project therefore moves through the following analytical progression:

```text
Descriptive statistics
        ↓
Visualization
        ↓
Correlation
        ↓
Regression
        ↓
Multivariate modeling
        ↓
ANOVA
        ↓
Post-hoc comparison
        ↓
Business interpretation
```

This is designed to demonstrate analytical maturity rather than simply producing charts.

---

# 🖥️ Streamlit Application

The Streamlit application provides three major analytical pages.

```text
Streamlit Application
│
├── Executive Dashboard
├── Weather & Geography
└── BI Questions
```

---

# 1️⃣ Executive Dashboard

The Executive Dashboard provides a high-level command-center view.

It combines:

- Executive KPIs
- Demand trends
- Time-of-day patterns
- Weekly patterns
- Business interpretation
- Analytical scope

The goal is to answer:

> **What is happening in the mobility system?**

before asking why it is happening.

---

# 2️⃣ Weather & Geography

The Weather & Geography page combines two analytical dimensions:

### Weather

- Temperature
- Rain
- Snow
- Wind
- Weather category
- Demand response

### Geography

- Pickup-zone demand
- High-demand zones
- Geographic concentration
- Spatial comparisons

This page answers:

> **Where is demand occurring, and how does the environment relate to demand?**

---

# 3️⃣ Business Intelligence Questions

The BI Questions page translates the underlying data into decision-oriented questions.

Instead of asking users to interpret every chart manually, the page structures analysis around business questions.

Examples include:

- What was the total taxi demand in 2021?
- What was average daily demand?
- Which months had the highest demand?
- Which hours experienced peak demand?
- Which weekdays were strongest?
- Which pickup zones generated the greatest demand?
- How much lower was demand during rain compared with dry conditions?
- How does snowfall compare with rainfall in terms of demand impact?
- What weather category produced the highest average daily revenue?
- How much revenue was associated with rainy days?
- What is the relationship between temperature and demand?
- What is the relationship between precipitation and demand?
- Which weather variable has the strongest observed relationship with demand?
- Does weather significantly differentiate average daily demand?
- What business questions cannot currently be answered from the available data?

The page is designed as a bridge between **analytics and decision support**.

---

# 🗺️ Spatial Analytics

Pickup zones provide a geographic view of mobility demand.

The project summarizes 257 pickup zones.

Spatial analysis is intentionally based on the geographic fields available in the analytical dataset.

The platform does not pretend to provide real-time fleet positioning because the current data does not contain real-time vehicle telemetry.

This distinction keeps the analysis grounded in actual evidence.

---

# 📦 Analytical Outputs

The statistical analysis pipeline generates reusable CSV outputs.

Examples include:

```text
daily_demand_confidence_interval.csv

dataset_validation.csv

hourly_demand_concentration.csv
hourly_demand_ranked.csv

monthly_demand_variability.csv
weekday_demand_variability.csv

multivariate_weather_coefficients.csv
multivariate_weather_diagnostics.csv
multivariate_weather_model.csv

pickup_zone_demand_ranked.csv
spatial_demand_concentration.csv

revenue_weather_effects.csv

statistical_findings_summary.csv

tukey_weather_comparisons.csv
weather_anova.csv
weather_correlations.csv
weather_effect_sizes.csv
weather_regressions.csv
weather_vif.csv
```

These outputs provide a reproducible analytical trail between the underlying data and the dashboard conclusions.

---

# 🔐 Security

The repository intentionally excludes local credentials and secrets.

The `.gitignore` protects files such as:

```text
.venv/
__pycache__/
*.py[cod]
.env
.streamlit/secrets.toml
service-account*.json
*-service-account*.json
.DS_Store
```

Google Cloud authentication is performed through local Application Default Credentials rather than embedding credentials inside the source code.

### Never commit

- Service-account JSON files
- API keys
- Passwords
- `.env` files
- Streamlit secrets
- OAuth credentials
- Private certificates

---

# ⚙️ Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/RASKOLNIKOV10884498/urban-mobility-analytics.git
cd urban-mobility-analytics
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

## 3. Activate the environment

macOS/Linux:

```bash
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## 5. Authenticate with Google Cloud

```bash
gcloud auth application-default login
```

The browser-based authentication process stores development credentials locally.

Credentials should never be committed to GitHub.

## 6. Run the application

```bash
streamlit run app.py
```

---

# 🌦️ Loading Weather Data

To refresh the 2021 weather dataset:

```bash
python ingest_weather.py
```

The ingestion script retrieves daily observations and loads them into:

```text
mobility_raw.daily_weather_2021
```

The weather data can then be combined with the analytical taxi summaries for downstream analysis.

---

# 🧪 Running Statistical Analysis

Run:

```bash
python analysis/statistical_analysis.py
```

The script performs validation and statistical analysis and writes analytical outputs under:

```text
analysis/outputs/
```

---

# 🛠️ Dependencies

The project uses a small set of core technologies.

| Technology | Purpose |
|---|---|
| Python | Application and analysis language |
| Pandas | Data manipulation |
| Google BigQuery | Cloud analytical warehouse |
| Streamlit | Interactive dashboard |
| Plotly | Interactive visualization |
| Requests | External weather API ingestion |
| SciPy / statistical tooling | Statistical analysis |

Dependencies are defined in:

```text
requirements.txt
```

---

# 🔄 Data Flow

The complete data lifecycle can be represented as:

```text
NYC Green Taxi Dataset
          │
          ▼
     BigQuery Raw Data
          │
          ▼
   Analytical SQL Models
          │
          ├──────────────► Monthly Summary
          ├──────────────► Hourly Summary
          ├──────────────► Weekday Summary
          └──────────────► Pickup Zone Summary

Open-Meteo API
          │
          ▼
   ingest_weather.py
          │
          ▼
     BigQuery Raw Weather
          │
          ▼
     Weather Analytics
          │
          ├──────────────► Weather Demand
          ├──────────────► Weather Revenue
          ├──────────────► Temperature
          ├──────────────► Rain
          ├──────────────► Snow
          └──────────────► Wind

All analytical tables
          │
          ▼
     Python data_loader
          │
          ▼
       metrics.py
          │
          ▼
       charts.py
          │
          ▼
      Streamlit pages
          │
          ▼
  Business Intelligence
```

---

# 🚀 Performance Design

The application is designed with cloud analytics performance in mind.

Instead of loading the full taxi trip dataset into Streamlit, the dashboard queries summarized analytical tables.

This provides several advantages:

- Smaller query results
- Faster dashboard loading
- Lower repeated query cost
- Cleaner application code
- Better separation between transformation and presentation
- Easier scalability

The pattern is:

```text
Large source dataset
        ↓
Cloud warehouse transformation
        ↓
Compact analytical tables
        ↓
Dashboard
```

This is preferable to performing expensive aggregation repeatedly inside the Streamlit UI.

---

# 🧩 Separation of Concerns

The repository deliberately separates responsibilities.

```text
BigQuery access
      ↓
Data loading
      ↓
Metrics
      ↓
Charts
      ↓
Streamlit pages
```

This allows individual layers to change without rewriting the entire application.

For example:

- A chart can change without changing BigQuery logic.
- A BigQuery table can be replaced without rewriting every chart.
- A metric can be centralized instead of duplicated.
- A new dashboard page can reuse existing data loaders and charts.

---

# 🧭 Data Quality and Validation

The statistical pipeline includes dataset validation before analysis.

Validation checks cover:

- Dataset dimensions
- Expected analytical structures
- Variable availability
- Numerical relationships
- Model diagnostics
- Multicollinearity diagnostics

The goal is to catch analytical problems before they become dashboard claims.

---

# ⚠️ Analytical Limitations

This project uses historical 2021 data.

Therefore, it should not be interpreted as a real-time representation of the current NYC transportation environment.

Important limitations include:

### Historical period

The core trip analysis covers 2021.

### Weather coverage

Weather variables are daily observations and therefore cannot fully represent minute-level weather changes across NYC.

### No real-time fleet telemetry

The project does not contain real-time vehicle locations.

### No driver availability data

The platform cannot directly determine whether demand changes were caused by driver supply constraints.

### No traffic telemetry

Congestion is not directly modeled.

### No causal identification

The statistical relationships are observational.

### Limited explanatory power

The weather regression model explains only a modest portion of daily demand variation.

These limitations are not hidden from the user; they are part of the analytical story.

---

# 🔮 Future Enhancements

The platform can be expanded substantially with additional datasets.

## Real-Time Mobility

Potential additions:

- Vehicle GPS
- Live fleet availability
- Trip status
- Pickup latency
- Driver supply

## Transportation Network

Potential additions:

- Subway disruptions
- Bus telemetry
- Traffic congestion
- Road closures
- Airport activity

## Weather Intelligence

Potential additions:

- Hourly weather
- Radar precipitation
- Severe-weather alerts
- Visibility
- Road conditions

## Economic Intelligence

Potential additions:

- Fuel prices
- Local economic indicators
- Employment data
- Consumer activity

## Event Intelligence

Potential additions:

- Concerts
- Sports events
- Festivals
- Holidays
- Conferences

These additions would make it possible to build substantially more sophisticated demand forecasting and scenario modeling.

---

# 🧠 What This Project Demonstrates

This repository is designed to demonstrate practical data-role capabilities.

### Data Engineering

- API ingestion
- Cloud storage
- Warehouse modeling
- Analytical table design

### SQL / Analytics Engineering

- Aggregation
- Dimensional summaries
- Analytical datasets
- Reusable warehouse structures

### Python

- Pandas
- Modular application design
- Statistical analysis
- API integration
- Data validation

### Statistics

- Correlation
- Regression
- Multivariate regression
- ANOVA
- Post-hoc analysis
- Effect sizes
- Confidence intervals
- VIF diagnostics

### Business Intelligence

- KPI design
- Decision-oriented questions
- Operational interpretation
- Revenue analysis
- Demand analysis

### Visualization

- Interactive Plotly charts
- Executive KPIs
- Temporal analysis
- Spatial analysis
- Weather analysis

### Cloud

- Google BigQuery
- Google Cloud authentication
- Cloud analytical architecture

### Application Development

- Streamlit
- Modular architecture
- Cached data loading
- Multi-page dashboard design

---

# 🧑‍💼 Business Value

A business intelligence system should ultimately help people make decisions.

The Urban Mobility Intelligence platform is designed around that principle.

Potential stakeholders include:

- Fleet operations teams
- Mobility analysts
- Transportation planners
- Revenue teams
- Business intelligence teams
- Data analysts
- Data scientists
- Urban mobility researchers

The dashboard helps stakeholders understand:

```text
Demand
  ↓
When does it happen?
  ↓
Where does it happen?
  ↓
What environmental conditions coincide with it?
  ↓
What happens to revenue?
  ↓
What evidence supports the conclusion?
  ↓
What additional data is needed?
```

---

# 📚 Reproducibility

A major objective of the repository is reproducibility.

The analytical workflow can be represented as:

```text
1. Configure environment
2. Authenticate to Google Cloud
3. Ingest weather
4. Build analytical summaries
5. Validate datasets
6. Run statistical analysis
7. Generate analytical outputs
8. Launch Streamlit
9. Explore business questions
```

The code, requirements, analytical outputs, and documentation are kept together so another developer can understand the intended workflow.

---

# 🔍 Example Analytical Narrative

A simplified analytical story from the project is:

> Taxi demand varies substantially across time and geography. Weather is associated with some of that variation, but weather alone does not explain the majority of daily demand changes.

Snowfall shows a stronger negative relationship with demand than precipitation or temperature.

Rainy days also show lower average daily gross customer charges than dry days.

However, the multivariate model explains less than 10% of daily demand variation, indicating that additional operational, economic, behavioral, and temporal variables are likely important.

This is more useful than claiming that weather "causes" demand changes.

---

# 🏆 Portfolio Positioning

This project is intentionally built to communicate more than dashboard-building ability.

It demonstrates an end-to-end analytical mindset:

```text
Question
  ↓
Data
  ↓
Warehouse
  ↓
Transformation
  ↓
Validation
  ↓
Statistics
  ↓
Visualization
  ↓
Business interpretation
```

That workflow reflects how modern analytics projects are often structured in professional environments.

---

# 📂 Repository Structure

```text
urban-mobility-analytics/
│
├── .gitignore
├── README.md
├── requirements.txt
│
├── app.py
├── bigquery.py
├── charts.py
├── data_loader.py
├── ingest_weather.py
├── metrics.py
│
├── analysis/
│   ├── statistical_analysis.py
│   └── outputs/
│       ├── daily_demand_confidence_interval.csv
│       ├── dataset_validation.csv
│       ├── hourly_demand_concentration.csv
│       ├── hourly_demand_ranked.csv
│       ├── monthly_demand_variability.csv
│       ├── multivariate_weather_coefficients.csv
│       ├── multivariate_weather_diagnostics.csv
│       ├── multivariate_weather_model.csv
│       ├── pickup_zone_demand_ranked.csv
│       ├── revenue_weather_effects.csv
│       ├── spatial_demand_concentration.csv
│       ├── statistical_findings_summary.csv
│       ├── tukey_weather_comparisons.csv
│       ├── weather_anova.csv
│       ├── weather_correlations.csv
│       ├── weather_effect_sizes.csv
│       ├── weather_regressions.csv
│       ├── weather_vif.csv
│       └── weekday_demand_variability.csv
│
└── pages/
    ├── 1_Executive_Dashboard.py
    ├── 2_Weather_Geography.py
    └── 3_BI_Questions.py
```

---

# 🛡️ Responsible Analytics

The project follows several principles.

### No fabricated metrics

If a metric cannot be calculated from the available data, it should not be presented as fact.

### No unsupported causal claims

Correlation and observational comparisons are not automatically causal effects.

### Transparent limitations

Known data limitations are documented.

### Reproducible analysis

Important calculations are represented in code or generated analytical outputs.

### Secure credentials

Cloud credentials remain outside the repository.

---

# 📌 Key Takeaways

The project demonstrates that a modern mobility analytics platform can combine:

- Cloud data warehousing
- Python
- SQL-oriented analytical modeling
- API ingestion
- Statistical analysis
- Interactive visualization
- Business intelligence
- Geographic analysis
- Revenue analysis
- Weather intelligence

The most important analytical conclusion is not simply that weather matters.

It is that **weather is one measurable component of a much larger mobility-demand system**.

The observed data supports meaningful weather-related insights, but it also clearly shows the limits of what can be explained using weather alone.

That distinction is central to the project's analytical design.

---

# 🚀 Roadmap

### Completed

- [x] BigQuery analytical warehouse
- [x] NYC Green Taxi 2021 summaries
- [x] Weather ingestion pipeline
- [x] Daily weather dataset
- [x] Monthly demand analysis
- [x] Hourly demand analysis
- [x] Weekday demand analysis
- [x] Pickup-zone analysis
- [x] Weather-demand analysis
- [x] Weather-revenue analysis
- [x] Statistical analysis
- [x] Regression analysis
- [x] ANOVA
- [x] Multivariate regression
- [x] Streamlit dashboard
- [x] Executive dashboard
- [x] Weather & Geography page
- [x] BI Questions page
- [x] Git repository

### Planned

- [ ] Add dashboard screenshots
- [ ] Deploy Streamlit application
- [ ] Add automated data-quality tests
- [ ] Add CI/CD
- [ ] Add scheduled weather refresh
- [ ] Add hourly weather
- [ ] Add demand forecasting
- [ ] Add scenario simulation
- [ ] Add additional mobility datasets
- [ ] Add richer geographic visualizations

---

# 👤 Author

**Anthony Nii Addo Nartey**

Urban Mobility Analytics is a portfolio project focused on demonstrating practical capabilities across data analytics, business intelligence, cloud data warehousing, statistical analysis, and interactive application development.

---

# 📜 License

This repository is intended as a portfolio and educational analytics project.

Dataset ownership and licensing remain with the respective data providers.

---

# ⭐ Final Perspective

Urban Mobility Intelligence is built around a simple idea:

> **A dashboard should not merely display data. It should help people understand what the data means, how confident they can be in the conclusion, and what they should investigate next.**

The project therefore connects the complete analytical chain:

```text
DATA
  ↓
WAREHOUSE
  ↓
MODELING
  ↓
VALIDATION
  ↓
STATISTICS
  ↓
VISUALIZATION
  ↓
BUSINESS QUESTIONS
  ↓
DECISION SUPPORT
```

That is the foundation of the Urban Mobility Intelligence platform.
