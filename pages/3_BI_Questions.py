


"""Business Intelligence and Decision Support for Urban Mobility Analytics."""

from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import (
    load_monthly_trips,
    load_hourly_trips,
    load_weekday_trips,
    load_pickup_zones,
    load_daily_weather,
    load_weather_impact,
    load_temperature_impact,
    load_precipitation_impact,
    load_snowfall_impact,
    load_wind_impact,
    load_weekday_weather_impact,
    load_revenue_weather_impact,
)

from metrics import (
    get_peak_month,
    get_peak_hour,
    get_peak_weekday,
    get_top_pickup_zone,
    get_weather_extremes,
)


st.set_page_config(
    page_title=" Operational insights| Urban Mobility Analytics",
    page_icon="📊",
    layout="wide",
)


monthly_trips = load_monthly_trips()
hourly_trips = load_hourly_trips()
weekday_trips = load_weekday_trips()
pickup_zones = load_pickup_zones()

daily_weather = load_daily_weather()

weather_impact = load_weather_impact()
temperature_impact = load_temperature_impact()
precipitation_impact = load_precipitation_impact()
snowfall_impact = load_snowfall_impact()
wind_impact = load_wind_impact()
weekday_weather = load_weekday_weather_impact()

revenue_weather = load_revenue_weather_impact()


def money(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "$0"
    return f"${float(value):,.0f}"


def money_precise(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "$0.00"
    return f"${float(value):,.2f}"


def number(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "0"
    return f"{float(value):,.0f}"


def pct(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "0.0%"
    return f"{float(value):.1f}%"


def signed_pct(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "0.0%"
    return f"{float(value):+.1f}%"


def signed_number(value: float) -> str:
    if value is None or not math.isfinite(float(value)):
        return "0"
    return f"{float(value):+,.0f}"


def safe_mean(
    dataframe: pd.DataFrame,
    column: str,
) -> float:
    if dataframe is None or dataframe.empty:
        return 0.0

    if column not in dataframe.columns:
        return 0.0

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return 0.0

    return float(values.mean())


def safe_sum(
    dataframe: pd.DataFrame,
    column: str,
) -> float:
    if dataframe is None or dataframe.empty:
        return 0.0

    if column not in dataframe.columns:
        return 0.0

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return 0.0

    return float(values.sum())


def safe_corr(
    dataframe: pd.DataFrame,
    x_column: str,
    y_column: str,
) -> float | None:
    if dataframe is None or dataframe.empty:
        return None

    if x_column not in dataframe.columns:
        return None

    if y_column not in dataframe.columns:
        return None

    values = dataframe[
        [x_column, y_column]
    ].copy()

    values[x_column] = pd.to_numeric(
        values[x_column],
        errors="coerce",
    )

    values[y_column] = pd.to_numeric(
        values[y_column],
        errors="coerce",
    )

    values = values.dropna()

    if len(values) < 2:
        return None

    correlation = values[x_column].corr(
        values[y_column]
    )

    if pd.isna(correlation):
        return None

    return float(correlation)


def weather_row(
    dataframe: pd.DataFrame,
    condition: str,
) -> pd.Series:
    if dataframe is None or dataframe.empty:
        return pd.Series(dtype="object")

    if "weather_condition" not in dataframe.columns:
        return pd.Series(dtype="object")

    rows = dataframe[
        dataframe["weather_condition"].astype(str).str.lower()
        == condition.lower()
    ]

    if rows.empty:
        return pd.Series(dtype="object")

    return rows.iloc[0]


def get_weather_value(
    dataframe: pd.DataFrame,
    condition: str,
    column: str,
) -> float | None:
    row = weather_row(
        dataframe,
        condition,
    )

    if row.empty:
        return None

    if column not in row.index:
        return None

    value = pd.to_numeric(
        pd.Series([row[column]]),
        errors="coerce",
    ).iloc[0]

    if pd.isna(value):
        return None

    return float(value)


def get_weather_impact_pct(
    dataframe: pd.DataFrame,
    condition: str,
) -> float | None:
    dry = get_weather_value(
        dataframe,
        "Dry",
        "avg_daily_trips",
    )

    target = get_weather_value(
        dataframe,
        condition,
        "avg_daily_trips",
    )

    if dry is None or target is None:
        return None

    if dry == 0:
        return None

    return (
        (target - dry)
        / dry
        * 100
    )


def get_revenue_weather_row(
    condition: str,
) -> pd.Series:
    return weather_row(
        revenue_weather,
        condition,
    )


def get_weighted_weather_metric(
    dataframe: pd.DataFrame,
    metric_column: str,
) -> float | None:
    if dataframe is None or dataframe.empty:
        return None

    if metric_column not in dataframe.columns:
        return None

    if "days_in_category" not in dataframe.columns:
        return safe_mean(
            dataframe,
            metric_column,
        )

    working = dataframe[
        [
            metric_column,
            "days_in_category",
        ]
    ].copy()

    working[metric_column] = pd.to_numeric(
        working[metric_column],
        errors="coerce",
    )

    working["days_in_category"] = pd.to_numeric(
        working["days_in_category"],
        errors="coerce",
    )

    working = working.dropna()

    if working.empty:
        return None

    denominator = working[
        "days_in_category"
    ].sum()

    if denominator == 0:
        return None

    return float(
        (
            working[metric_column]
            * working["days_in_category"]
        ).sum()
        / denominator
    )


def get_weather_annual_total(
    dataframe: pd.DataFrame,
    daily_metric_column: str,
) -> float | None:
    if dataframe is None or dataframe.empty:
        return None

    required = [
        daily_metric_column,
        "days_in_category",
    ]

    if not all(
        column in dataframe.columns
        for column in required
    ):
        return None

    working = dataframe[
        required
    ].copy()

    working[daily_metric_column] = pd.to_numeric(
        working[daily_metric_column],
        errors="coerce",
    )

    working["days_in_category"] = pd.to_numeric(
        working["days_in_category"],
        errors="coerce",
    )

    working = working.dropna()

    if working.empty:
        return None

    return float(
        (
            working[daily_metric_column]
            * working["days_in_category"]
        ).sum()
    )


def get_days_in_weather_category(
    dataframe: pd.DataFrame,
    condition: str,
) -> float:
    value = get_weather_value(
        dataframe,
        condition,
        "days_in_category",
    )

    return value or 0.0


def classify_correlation(
    correlation: float | None,
) -> str:
    if correlation is None:
        return "not available"

    absolute = abs(correlation)

    if absolute >= 0.70:
        strength = "strong"
    elif absolute >= 0.40:
        strength = "moderate"
    elif absolute >= 0.20:
        strength = "weak"
    else:
        strength = "very weak"

    direction = (
        "positive"
        if correlation > 0
        else "negative"
        if correlation < 0
        else "neutral"
    )

    return f"{strength} {direction}"


def render_answer(
    title: str,
    answer: str,
    interpretation: str,
    evidence: str,
    calculation: str,
    implication: str,
    limitation: str,
) -> None:
    with st.expander(
        f"**{title}**",
        expanded=False,
    ):
        st.markdown(
            "### Answer"
        )

        st.markdown(answer)

        st.markdown(
            "### Business interpretation"
        )

        st.markdown(interpretation)

        st.markdown(
            "### Evidence from the current data"
        )

        st.markdown(evidence)

        st.markdown(
            "### Calculation"
        )

        st.markdown(calculation)

        st.markdown(
            "### Decision implication"
        )

        st.markdown(implication)

        st.markdown(
            "### Analytical limitation"
        )

        st.markdown(limitation)


def render_unavailable(
    title: str,
    reason: str,
) -> None:
    with st.expander(
        f"**{title}**",
        expanded=False,
    ):
        st.warning(
            "This question cannot be answered reliably "
            "from the currently loaded data."
        )

        st.markdown(
            reason
        )


st.sidebar.title(
    "🎯 Action Center"
)

st.sidebar.markdown(
    """
    This decision-support layer converts the current
    historical mobility and weather warehouse into
    questions that can be answered directly from the
    available analytical tables.

    The emphasis is on measurable evidence.

    The dashboard does not create answers for datasets
    that are not present.
    """
)

rain_demand_change = get_weather_impact_pct(
    weather_impact,
    "Rain",
)

snow_demand_change = get_weather_impact_pct(
    weather_impact,
    "Snow",
)

dry_revenue = get_weather_value(
    revenue_weather,
    "Dry",
    "avg_daily_gross_customer_charges_usd",
)

rain_revenue = get_weather_value(
    revenue_weather,
    "Rain",
    "avg_daily_gross_customer_charges_usd",
)

snow_revenue = get_weather_value(
    revenue_weather,
    "Snow",
    "avg_daily_gross_customer_charges_usd",
)

if rain_demand_change is not None:
    if rain_demand_change < 0:
        st.sidebar.info(
            f"""
            **Rain response**

            Historical rain days are associated with
            approximately **{abs(rain_demand_change):.1f}%**
            lower average daily taxi demand than dry days.

            The appropriate operational response is to
            monitor demand forecasts and prepare for a
            potential reduction in trip volume.
            """
        )
    else:
        st.sidebar.info(
            f"""
            **Rain response**

            Historical rain days are associated with
            approximately **{rain_demand_change:.1f}%**
            higher average daily demand than dry days.

            Historical conditions should therefore be
            monitored rather than assuming rain always
            reduces demand.
            """
        )

if snow_demand_change is not None:
    if snow_demand_change < 0:
        st.sidebar.warning(
            f"""
            **Snow response**

            Historical snow conditions are associated
            with approximately **{abs(snow_demand_change):.1f}%**
            lower average daily demand than dry days.

            Severe-weather readiness should account for
            this historical demand change.
            """
        )

if pickup_zones is not None and not pickup_zones.empty:
    top_zone = get_top_pickup_zone(
        pickup_zones
    )

    if top_zone is not None and not top_zone.empty:
        top_zone_name = top_zone.get(
            "pickup_zone",
            "Unknown",
        )

        top_zone_trips = top_zone.get(
            "total_trips",
            0,
        )

        st.sidebar.success(
            f"""
            **Demand concentration**

            **{top_zone_name}** is the current highest-volume
            pickup zone.

            Recorded annual trips:
            **{number(top_zone_trips)}**

            This is a useful starting point for future
            capacity and spatial analysis.
            """
        )

st.sidebar.divider()

st.sidebar.caption(
    "Current analysis uses historical taxi and weather "
    "data. Real-time routing, transit telemetry, "
    "micro-mobility telemetry, EV telemetry, radar, "
    "and incident feeds are outside the current scope."
)


st.title(
    "📊 Business Intelligence & Decision Support"
)

st.markdown(
    """
    # Urban Mobility Intelligence

    This page is the business-intelligence layer of the
    Urban Mobility Analytics platform.

    Rather than presenting isolated charts, the page is
    organized around a set of explicit business questions.

    Each question opens into a complete analytical response.

    The purpose is to move from:

    **data → measurement → interpretation → decision**

    The current analytical model focuses on 2021 taxi
    activity and daily weather conditions.

    The dashboard intentionally avoids claiming that the
    available data can answer questions about public
    transportation, micro-mobility, real-time traffic,
    EV fleets, or future climate conditions.

    The result is a narrower but more defensible BI product.
    """
)

st.markdown(
    """
    ## The four-layer analytical architecture

    ### Layer 1 — Executive Pulse

    The Executive Pulse answers questions about the overall
    health of taxi demand, revenue, weather exposure, and
    operational performance.

    This layer is intended for a decision-maker who wants
    the answer before looking at the underlying chart.

    ### Layer 2 — Correlative Engine

    The Correlative Engine examines relationships between
    demand and environmental conditions.

    Temperature, precipitation, snowfall, wind, weekday
    behavior, revenue, and trip volume can be compared
    through the available historical observations.

    ### Layer 3 — Spatial Ground-Truth

    The Spatial Ground-Truth layer focuses on pickup-zone
    demand.

    It tells us where taxi activity is concentrated.

    It does not claim that those zones have different
    rainfall levels because the current weather source is
    city-level rather than a weather observation attached
    to every pickup zone.

    ### Layer 4 — Scenario Simulator

    The Scenario Simulator uses observed historical weather
    categories as scenarios.

    It answers questions such as:

    "What does historical average demand look like during
    rain compared with dry conditions?"

    It does not claim to be a future forecasting model.
    """
)

st.markdown(
    """
    ## How to read this page

    Every question below is presented as a collapsible
    decision-support card.

    Open a question to see:

    - the direct answer
    - the business interpretation
    - the evidence
    - the calculation
    - the decision implication
    - the analytical limitation

    The objective is to make every answer traceable to
    something the warehouse actually contains.

    A good BI dashboard should be able to say both:

    "Here is what the data tells us."

    and:

    "Here is what the data does not tell us."

    That distinction is central to this page.
    """
)

st.divider()


st.header(
    "1️⃣ Executive Pulse"
)

st.markdown(
    """
    The Executive Pulse provides the highest-level view
    of the mobility system represented in the current
    warehouse.

    The questions in this section focus on demand volume,
    revenue, tips, and the overall financial relationship
    with weather.

    These are the questions most suitable for a senior
    decision-maker who needs a concise description of
    system performance.
    """
)


total_trips = safe_sum(
    daily_weather,
    "total_trips",
)

average_daily_trips = safe_mean(
    daily_weather,
    "total_trips",
)

average_daily_revenue = get_weighted_weather_metric(
    revenue_weather,
    "avg_daily_gross_customer_charges_usd",
)

average_daily_tips = get_weighted_weather_metric(
    revenue_weather,
    "avg_daily_tips_usd",
)


# ================================================================
# EXECUTIVE BI QUESTIONS
# ================================================================
# The dashboard keeps the existing collapsible-card structure.
# The questions below are deliberately tied to metrics that are
# available in the current warehouse and validated by the
# statistical-analysis layer.

# ----------------------------------------------------------------
# Q1 — Typical daily demand
# ----------------------------------------------------------------
q1_answer = f"""
The mobility system represented by the current 2021 analytical
warehouse handled an average of approximately **{number(average_daily_trips)}
taxi trips per day**.

That is the most useful definition of a normal operating day in
this dashboard because it is based on the complete set of daily
observations rather than on a single unusually busy or quiet day.
"""

q1_interpretation = """
A senior decision-maker usually needs to know the operating scale
before looking at individual weather events, locations, or time
periods. The average daily demand provides that baseline.

The important distinction is between the total number of trips in
the dataset and the number of trips a typical day represents. The
annual total tells us the scale of the historical observation set,
while the daily average gives us a practical benchmark against
which other operating conditions can be compared.

This baseline becomes particularly useful later in the dashboard.
If a weather condition produces 2,250 trips while a normal day
produces roughly 2,786, the difference is immediately understandable
as a departure from normal operating volume rather than simply as
another raw number.

The metric therefore acts as the reference point for demand
planning, scenario analysis, and the interpretation of weather
exposure.
"""

q1_evidence = f"""
The dashboard calculates the mean directly from the `total_trips`
field in the daily weather-demand dataset.

**Observed average: {number(average_daily_trips)} trips/day**

The underlying analytical table contains **{number(len(daily_weather))}
daily observations** after the data loader returns the warehouse
result.

This same daily dataset is used for the weather correlations,
confidence interval, and weather-category analysis later on the
page.
"""

q1_calculation = """
The calculation is:

**Average daily demand = MEAN(daily `total_trips`)**

Values are converted to numeric form and invalid observations are
removed before the mean is calculated. Missing values are therefore
not silently interpreted as zero-demand days.
"""

q1_implication = """
This benchmark gives operations a definition of a normal historical
day. It can be used as a reference when evaluating staffing,
fleet availability, revenue expectations, and weather scenarios.

It also provides context for the other dashboard questions. A
percentage change is much more meaningful when management can see
the underlying daily operating scale.
"""

q1_limitation = """
This is a taxi-demand benchmark, not a measure of every form of
urban mobility. It does not represent subway, bus, bike, scooter,
private vehicle, or ride-hailing activity that is outside the
current warehouse.
"""

render_answer(
    "1. How much demand does the mobility system handle on a typical day?",
    q1_answer,
    q1_interpretation,
    q1_evidence,
    q1_calculation,
    q1_implication,
    q1_limitation,
)


# ----------------------------------------------------------------
# Q2 — Peak operating hour
# ----------------------------------------------------------------
q2_peak_hour = None
q2_peak_trips = None
if (
    hourly_trips is not None
    and not hourly_trips.empty
    and "pickup_hour" in hourly_trips.columns
    and "total_trips" in hourly_trips.columns
):
    hourly_working = hourly_trips[["pickup_hour", "total_trips"]].copy()
    hourly_working["pickup_hour"] = pd.to_numeric(
        hourly_working["pickup_hour"], errors="coerce"
    )
    hourly_working["total_trips"] = pd.to_numeric(
        hourly_working["total_trips"], errors="coerce"
    )
    hourly_working = hourly_working.dropna()
    if not hourly_working.empty:
        peak_row = hourly_working.loc[
            hourly_working["total_trips"].idxmax()
        ]
        q2_peak_hour = int(peak_row["pickup_hour"])
        q2_peak_trips = float(peak_row["total_trips"])

if q2_peak_hour is not None:
    q2_answer = f"""
**{q2_peak_hour}:00 is the busiest hour represented in the hourly
historical demand table**, with approximately **{number(q2_peak_trips)}
trips**.

The result identifies the point in the daily operating cycle where
historical taxi demand reaches its highest observed hourly volume.
"""
else:
    q2_answer = """
The hourly demand table does not currently contain enough valid
information to identify the peak operating hour.
"""

q2_interpretation = """
Peak-hour analysis turns the daily demand benchmark into an
operational timetable.

Knowing that the system averages thousands of trips per day is useful,
but it does not tell an operations team when that demand arrives.
Hourly concentration reveals whether demand is distributed evenly
throughout the day or whether particular periods place substantially
greater pressure on the system.

The current data shows a clear peak rather than a flat demand curve.
That matters because capacity requirements are usually determined by
high-demand periods, not by the daily average alone.

A fleet or staffing plan built only around average daily demand could
therefore underestimate the resources required during the busiest
part of the day.
"""

q2_evidence = f"""
The dashboard evaluates the hourly analytical table and selects the
row with the maximum `total_trips` value.

**Peak hour: {f'{q2_peak_hour}:00' if q2_peak_hour is not None else 'not available'}**

**Trips during peak hour: {number(q2_peak_trips or 0)}**

The hourly table contains **{number(len(hourly_trips) if hourly_trips is not None else 0)}
hourly records**.
"""

q2_calculation = """
The calculation is:

**Peak hour = ARGMAX(total_trips grouped by pickup_hour)**

The associated `total_trips` value is retained as the peak-hour
volume.
"""

q2_implication = """
The peak period is a natural candidate for capacity planning,
fleet positioning, staffing, and monitoring.

If the organization later adds live telemetry, this historical peak
can become a benchmark against which real-time demand can be compared.
The current result is therefore useful even though the warehouse is
historical rather than real-time.
"""

q2_limitation = """
The result identifies the busiest historical hour in the aggregated
hourly table. It does not show how demand varies by individual
pickup zone within that hour, nor does it provide real-time vehicle
availability.
"""

render_answer(
    "2. When does demand reach its daily peak?",
    q2_answer,
    q2_interpretation,
    q2_evidence,
    q2_calculation,
    q2_implication,
    q2_limitation,
)


# ----------------------------------------------------------------
# Q3 — Hourly concentration
# ----------------------------------------------------------------
q3_top5_share = None
q3_top10_share = None
if (
    hourly_trips is not None
    and not hourly_trips.empty
    and "total_trips" in hourly_trips.columns
):
    hourly_values = pd.to_numeric(
        hourly_trips["total_trips"], errors="coerce"
    ).dropna()
    if not hourly_values.empty and hourly_values.sum() != 0:
        q3_top5_share = hourly_values.nlargest(5).sum() / hourly_values.sum() * 100
        q3_top10_share = hourly_values.nlargest(10).sum() / hourly_values.sum() * 100

if q3_top5_share is not None:
    q3_answer = f"""
The busiest periods account for a substantial share of the observed
hourly demand.

The **top 5 hours account for approximately {q3_top5_share:.2f}%** of
all trips represented in the hourly demand table, while the **top 10
hours account for approximately {q3_top10_share:.2f}%**.

This means demand is meaningfully concentrated rather than being
evenly distributed across all 24 hours.
"""
else:
    q3_answer = """
The current hourly demand table does not contain enough valid data to
calculate hourly concentration.
"""

q3_interpretation = """
Concentration matters because two systems can have the same total
number of trips but very different operational difficulty.

A system with evenly distributed demand can operate closer to its
average capacity throughout the day. A concentrated system has to
absorb much more activity during particular periods while carrying
less activity during quieter periods.

The current data demonstrates the second pattern. The busiest five
hours represent more than one-third of all hourly trips. That is a
strong operational signal because it means a meaningful portion of
annual demand is compressed into a relatively small portion of the
day.

This is exactly the kind of insight that an executive dashboard
should surface: the issue is not only how much demand exists, but
when that demand arrives.
"""

q3_evidence = f"""
The hourly table contains **{number(len(hourly_trips) if hourly_trips is not None else 0)}
records and a `total_trips` measure.

**Top-5-hour share: {q3_top5_share:.2f}%**

**Top-10-hour share: {q3_top10_share:.2f}%**

These values are calculated from the ranked hourly trip volumes.
"""

q3_calculation = """
The calculation is:

**Top-N concentration = SUM(top N hourly trip totals) / SUM(all hourly trip totals) × 100**

The dashboard calculates this separately for the top five and top
ten hours.
"""

q3_implication = """
The concentration profile supports time-based capacity planning.
Resources do not necessarily need to be distributed evenly across
all hours if the historical demand pattern is strongly concentrated.

A future operational model could combine this hourly concentration
with pickup-zone concentration to identify when and where the system
is under the greatest historical demand pressure.
"""

q3_limitation = """
This is an aggregate hourly pattern. It does not identify the exact
vehicles, drivers, queues, or unmet demand behind the observed trip
volume. It also does not prove that the same concentration would
exist in a different year.
"""

render_answer(
    "3. How concentrated is demand around the busiest hours?",
    q3_answer,
    q3_interpretation,
    q3_evidence,
    q3_calculation,
    q3_implication,
    q3_limitation,
)


# ----------------------------------------------------------------
# Q4 — Spatial concentration
# ----------------------------------------------------------------
q4_top5_share = None
q4_top10_share = None
q4_median_zone = None
q4_top_zone_name = None
q4_top_zone_trips = None
if (
    pickup_zones is not None
    and not pickup_zones.empty
    and "total_trips" in pickup_zones.columns
):
    zone_working = pickup_zones.copy()
    zone_working["total_trips"] = pd.to_numeric(
        zone_working["total_trips"], errors="coerce"
    )
    zone_working = zone_working.dropna(subset=["total_trips"])
    if not zone_working.empty and zone_working["total_trips"].sum() != 0:
        ranked_zones = zone_working.sort_values("total_trips", ascending=False)
        zone_total = ranked_zones["total_trips"].sum()
        q4_top5_share = ranked_zones.head(5)["total_trips"].sum() / zone_total * 100
        q4_top10_share = ranked_zones.head(10)["total_trips"].sum() / zone_total * 100
        q4_median_zone = float(ranked_zones["total_trips"].median())
        if "pickup_zone" in ranked_zones.columns:
            q4_top_zone_name = ranked_zones.iloc[0]["pickup_zone"]
        q4_top_zone_trips = float(ranked_zones.iloc[0]["total_trips"])

if q4_top5_share is not None:
    q4_answer = f"""
Yes. Taxi demand is strongly concentrated geographically.

The **top 5 pickup zones account for approximately {q4_top5_share:.2f}%**
of all trips represented in the pickup-zone table. The **top 10 account
for approximately {q4_top10_share:.2f}%**.

The highest-volume zone is **{q4_top_zone_name}**, with approximately
**{number(q4_top_zone_trips)} recorded trips**.

The median pickup-zone volume is approximately **{number(q4_median_zone)}
trips**, illustrating the difference between the typical zone and the
highest-volume locations.
"""
else:
    q4_answer = """
The current pickup-zone table does not contain enough valid information
to calculate spatial demand concentration.
"""

q4_interpretation = """
Spatial concentration is one of the strongest operational insights in
the warehouse because it shows that demand is not distributed evenly
across the city.

A small group of pickup zones represents a large share of the recorded
activity. That means the operational importance of locations is highly
uneven: some zones contribute substantially more trips than others.

This matters for capacity planning, service coverage, infrastructure
prioritization, and future location-based analytics. If additional
real-time data becomes available later, these high-volume zones would
be natural places to monitor for congestion, vehicle availability, or
service pressure.

Importantly, this is a demand-concentration finding. It should not be
turned into a claim that those zones receive more rain because the
current weather observations are city-level rather than zone-level.
"""

q4_evidence = f"""
The dashboard ranks the **257 pickup zones** by `total_trips`.

**Top 5 zone share: {q4_top5_share:.2f}%**

**Top 10 zone share: {q4_top10_share:.2f}%**

**Median zone trips: {number(q4_median_zone or 0)}**

**Highest-volume zone: {q4_top_zone_name if q4_top_zone_name is not None else 'not available'}**
"""

q4_calculation = """
The concentration calculation is:

**Top-N zone share = SUM(trips in top N zones) / SUM(trips in all zones) × 100**

The dashboard ranks zones first and then calculates the top-five and
top-ten shares.
"""

q4_implication = """
The concentration profile can guide where future operational
intelligence should be focused.

High-volume zones are natural candidates for deeper analysis once
additional data sources are introduced. For example, real-time
traffic, incident, vehicle-position, or curb-availability data could
be joined to these locations to turn static spatial concentration into
live operational intelligence.
"""

q4_limitation = """
The current data establishes where taxi demand is concentrated. It does
not establish congestion, unmet demand, driver availability, or local
rainfall differences. Weather is not observed separately for each
pickup zone in the current warehouse.
"""

render_answer(
    "4. Is demand heavily concentrated in a small number of pickup zones?",
    q4_answer,
    q4_interpretation,
    q4_evidence,
    q4_calculation,
    q4_implication,
    q4_limitation,
)


# ----------------------------------------------------------------
# Q5 — Monthly variability
# ----------------------------------------------------------------
q5_month_cv = None
q5_month_min = None
q5_month_max = None
if (
    monthly_trips is not None
    and not monthly_trips.empty
    and "total_trips" in monthly_trips.columns
):
    monthly_values = pd.to_numeric(
        monthly_trips["total_trips"], errors="coerce"
    ).dropna()
    if not monthly_values.empty and monthly_values.mean() != 0:
        q5_month_cv = monthly_values.std(ddof=1) / monthly_values.mean() * 100
        q5_month_min = float(monthly_values.min())
        q5_month_max = float(monthly_values.max())

if q5_month_cv is not None:
    q5_answer = f"""
Monthly demand is **meaningfully variable but not wildly unstable**.

The coefficient of variation is approximately **{q5_month_cv:.2f}%**.
Across the twelve monthly observations, demand ranges from
**{number(q5_month_min)} to {number(q5_month_max)} trips**.

This means the system has a recognizable seasonal operating range,
with some months substantially busier than others.
"""
else:
    q5_answer = """
The monthly demand table does not contain enough valid observations to
calculate monthly demand variability.
"""

q5_interpretation = """
Average demand alone can hide seasonal movement. Monthly variability
shows whether the historical system operated at roughly the same scale
throughout the year or whether certain months carried substantially
more or less demand.

The current coefficient of variation of roughly 14.5% indicates that
monthly demand is not constant. The difference between the lowest and
highest months is large enough to matter operationally, but the system
is not characterized by extreme month-to-month instability.

This distinction is useful for management because it suggests that a
single annual average is insufficient for planning. Seasonal baselines
can provide a more realistic expectation of normal demand depending on
the time of year.
"""

q5_evidence = f"""
The monthly analytical dataset contains **{number(len(monthly_trips) if monthly_trips is not None else 0)}
monthly observations.

**Coefficient of variation: {q5_month_cv:.2f}%**

**Minimum monthly demand: {number(q5_month_min or 0)} trips**

**Maximum monthly demand: {number(q5_month_max or 0)} trips**
"""

q5_calculation = """
The coefficient of variation is:

**CV = sample standard deviation of monthly trips / mean monthly trips × 100**

It expresses monthly dispersion relative to the average, making the
measure easier to compare with other variability measures.
"""

q5_implication = """
Seasonal planning should therefore use monthly expectations rather
than relying exclusively on the annual average.

A future forecasting layer could incorporate month, weekday, hour, and
weather simultaneously to produce a much more precise expected-demand
baseline.
"""

q5_limitation = """
The result is based on twelve monthly observations from the historical
period. It describes the observed year and should not automatically be
treated as a multi-year seasonal pattern.
"""

render_answer(
    "5. How stable is demand from month to month?",
    q5_answer,
    q5_interpretation,
    q5_evidence,
    q5_calculation,
    q5_implication,
    q5_limitation,
)


# ----------------------------------------------------------------
# Q6 — Weekday variability
# ----------------------------------------------------------------
q6_weekday_cv = None
q6_weekday_min = None
q6_weekday_max = None
if (
    weekday_trips is not None
    and not weekday_trips.empty
    and "total_trips" in weekday_trips.columns
):
    weekday_values = pd.to_numeric(
        weekday_trips["total_trips"], errors="coerce"
    ).dropna()
    if not weekday_values.empty and weekday_values.mean() != 0:
        q6_weekday_cv = weekday_values.std(ddof=1) / weekday_values.mean() * 100
        q6_weekday_min = float(weekday_values.min())
        q6_weekday_max = float(weekday_values.max())

if q6_weekday_cv is not None:
    q6_answer = f"""
Demand also varies across the weekly operating cycle.

The weekday coefficient of variation is approximately
**{q6_weekday_cv:.2f}%**, with observed weekday demand ranging from
**{number(q6_weekday_min)} to {number(q6_weekday_max)} trips**.

The weekly pattern therefore represents a meaningful source of demand
variation alongside weather and seasonality.
"""
else:
    q6_answer = """
The weekday demand table does not contain enough valid observations to
calculate weekday variability.
"""

q6_interpretation = """
Weekday variability is operationally important because demand does not
simply reset to the same level every day.

A Monday, Wednesday, Saturday, or Sunday can represent a different
operating environment even before weather is considered. That means a
weather comparison can be misleading if weekday structure is ignored.

This is why the dashboard's weather analysis includes a dedicated
weekday-weather interaction table. The goal is to understand weather
within the context of normal weekly demand rather than treating every
day as interchangeable.

The observed weekday variability also explains why a future demand
model should include calendar features alongside environmental
features.
"""

q6_evidence = f"""
The weekday analytical dataset contains **{number(len(weekday_trips) if weekday_trips is not None else 0)}
weekday observations.

**Coefficient of variation: {q6_weekday_cv:.2f}%**

**Lowest weekday volume: {number(q6_weekday_min or 0)} trips**

**Highest weekday volume: {number(q6_weekday_max or 0)} trips**
"""

q6_calculation = """
The calculation is:

**Weekday CV = sample standard deviation of weekday trips / mean weekday trips × 100**

The result measures how widely weekday demand varies around the
weekday average.
"""

q6_implication = """
Operational planning should consider calendar structure before
interpreting weather changes.

A stronger forecasting system would therefore combine weekday and
weather rather than using a single weather-response rule for every day.
"""

q6_limitation = """
The calculation describes the aggregated weekday pattern in the
historical dataset. It does not isolate holidays, special events, or
individual dates that may contribute to the observed differences.
"""

render_answer(
    "6. How much does demand vary across the week?",
    q6_answer,
    q6_interpretation,
    q6_evidence,
    q6_calculation,
    q6_implication,
    q6_limitation,
)


# ----------------------------------------------------------------
# Q7 — Strongest weather relationship
# ----------------------------------------------------------------
q7_weather_correlations = {}
for variable, label in [
    ("avg_temperature_f", "Temperature"),
    ("precipitation_inches", "Precipitation"),
    ("snowfall_inches", "Snowfall"),
    ("max_wind_speed_mph", "Wind"),
]:
    corr_value = safe_corr(daily_weather, variable, "total_trips")
    if corr_value is not None:
        q7_weather_correlations[label] = corr_value

if q7_weather_correlations:
    q7_strongest = max(
        q7_weather_correlations,
        key=lambda key: abs(q7_weather_correlations[key]),
    )
    q7_strongest_corr = q7_weather_correlations[q7_strongest]
    q7_answer = f"""
Among the weather variables tested, **{q7_strongest.lower()} has the
strongest observed relationship with daily taxi demand**.

Its Pearson correlation with daily trips is **{q7_strongest_corr:.3f}**.
The relationship is **{classify_correlation(q7_strongest_corr)}**.

In the current historical analysis, snowfall is the strongest weather
signal, with a negative relationship to demand.
"""
else:
    q7_answer = """
The current daily weather dataset does not contain enough valid paired
observations to compare the weather variables.
"""

q7_interpretation = """
This question compares weather variables rather than examining them in
isolation.

That distinction matters because temperature, precipitation, snowfall,
and wind do not have equal relationships with observed taxi demand.
Ranking the absolute correlation values identifies which environmental
measure has the strongest simple linear association in the available
historical data.

The result is particularly useful because snowfall stands out from the
other variables. Its negative relationship is stronger than the
relationships observed for temperature, precipitation, or wind.

However, the size of a correlation should not be confused with a
causal effect. A weather variable can be correlated with other seasonal
and calendar conditions. The statistical result tells us which signal
is strongest in this dataset, not that the variable operates alone.
"""

q7_evidence = """
The daily weather table provides four environmental variables that can
be compared against `total_trips`:

- average temperature
- precipitation
- snowfall
- maximum wind speed

The validated statistical analysis produced these Pearson
relationships:

- **Temperature: r = 0.120**
- **Precipitation: r = -0.133**
- **Snowfall: r = -0.283**
- **Wind: r = -0.037**

Snowfall therefore has the largest absolute correlation.
"""

q7_calculation = """
For each weather variable, the dashboard calculates:

**Pearson correlation = corr(weather variable, daily total trips)**

The variables are then ranked by the absolute value of the correlation
coefficient to identify the strongest observed linear relationship.
"""

q7_implication = """
Snowfall should receive particular attention in historical weather
scenario planning because it is the strongest environmental signal in
the current demand data.

This does not mean other variables should be discarded. A production
forecasting model should retain multiple predictors and evaluate them
jointly rather than selecting one variable solely from a correlation
ranking.
"""

q7_limitation = """
Correlation measures association, not causation. It also measures a
simple pairwise relationship and does not account for all other
variables simultaneously.
"""

render_answer(
    "7. Which weather factor has the strongest relationship with trip demand?",
    q7_answer,
    q7_interpretation,
    q7_evidence,
    q7_calculation,
    q7_implication,
    q7_limitation,
)


# ----------------------------------------------------------------
# Q8 — Precipitation relationship
# ----------------------------------------------------------------
q8_precip_corr = safe_corr(
    daily_weather,
    "precipitation_inches",
    "total_trips",
)
if q8_precip_corr is not None:
    q8_answer = f"""
**Yes.** Precipitation is associated with lower daily taxi demand in
the historical data.

The Pearson correlation is **{q8_precip_corr:.3f}**, indicating a
**{classify_correlation(q8_precip_corr)} relationship** between daily
precipitation and daily trips.

The validated statistical analysis also found this relationship to be
statistically significant, with **p = 0.010866**.
"""
else:
    q8_answer = """
The current daily weather dataset does not contain enough valid paired
precipitation and demand observations to calculate the relationship.
"""

q8_interpretation = """
The precipitation result provides a measurable signal that rainfall
conditions and taxi demand do not move independently in the observed
historical period.

The relationship is negative, meaning that days with greater
precipitation tend to be associated with lower observed trip volume.
The relationship is statistically significant, but it is still weak in
magnitude. That distinction is important.

A statistically significant result does not automatically mean that
precipitation explains a large portion of demand. In this case, the
simple precipitation regression explains only a small amount of the
variation in daily trips.

The business interpretation should therefore be that precipitation is
a relevant historical indicator, but not a complete explanation of
mobility demand.
"""

q8_evidence = """
The validated statistical analysis used **365 daily observations**.

For precipitation versus daily trips:

- **Pearson r = -0.1332**
- **Pearson p = 0.010866**
- **Spearman rho = -0.1234**
- **Spearman p = 0.018340**
- simple regression **R² = 0.0177**

Both correlation methods indicate a weak negative association.
"""

q8_calculation = """
The dashboard measures the pairwise relationship between:

**`precipitation_inches` → `total_trips`**

using Pearson correlation, while the statistical-analysis layer also
checks the relationship using Spearman correlation and simple linear
regression.
"""

q8_implication = """
Precipitation can reasonably be included as an explanatory feature in
a future demand model.

However, it should not be used as a standalone demand forecast. The
stronger operational approach is to combine precipitation with
snowfall, temperature, weekday, hour, month, and other available
features.
"""

q8_limitation = """
The result is observational and does not establish that precipitation
alone caused the reduction in trips. The effect size is also weak, so
precipitation should be interpreted as one factor among several.
"""

render_answer(
    "8. Does precipitation correspond with lower mobility demand?",
    q8_answer,
    q8_interpretation,
    q8_evidence,
    q8_calculation,
    q8_implication,
    q8_limitation,
)


# ----------------------------------------------------------------
# Q9 — Temperature usefulness
# ----------------------------------------------------------------
q9_temp_corr = safe_corr(
    daily_weather,
    "avg_temperature_f",
    "total_trips",
)
if q9_temp_corr is not None:
    q9_answer = f"""
Temperature has a **weak positive relationship** with daily taxi
demand, but it is not a powerful standalone predictor.

The Pearson correlation is **{q9_temp_corr:.3f}**. The validated
regression explains only about **1.44% of the variation in daily trips**
using temperature alone.

The individual temperature coefficient was statistically significant
in the simple model (**p = 0.022013**), but the effect size remains
small.
"""
else:
    q9_answer = """
The current weather dataset does not contain enough valid observations
to evaluate temperature against daily demand.
"""

q9_interpretation = """
Temperature is a useful example of why statistical significance and
business significance are not the same thing.

The relationship is statistically detectable in the historical data,
but the correlation is weak and the simple model explains only a small
fraction of daily demand variation.

That means temperature should not be presented as a major standalone
demand driver. Instead, it is better understood as one environmental
feature that may become useful when combined with other variables.

Temperature also changes systematically with season, which means a
simple temperature-demand relationship can partially reflect broader
seasonal structure. A more sophisticated model could test temperature
bands or nonlinear relationships instead of assuming that every one
degree change has the same operational meaning.
"""

q9_evidence = """
The validated statistical analysis used **365 daily observations**.

Temperature versus daily trips:

- **Pearson r = 0.1199**
- **Pearson p = 0.022013**
- simple regression **R² = 0.0144**
- coefficient = **4.5841 trips per degree Fahrenheit**

The multivariate model later reduces the independent significance of
temperature once the other weather variables are considered jointly.
"""

q9_calculation = """
The dashboard calculates:

**Pearson correlation between `avg_temperature_f` and `total_trips`**

The statistical analysis additionally evaluates a simple linear model
and a multivariate weather model.
"""

q9_implication = """
Temperature is suitable for inclusion in future forecasting and
scenario models, but it should be combined with other predictors.

The result supports a richer environmental model rather than a
single-variable temperature forecast.
"""

q9_limitation = """
Temperature is correlated with season and other environmental
conditions. The observed relationship therefore should not be read as
a causal temperature effect on taxi demand.
"""

render_answer(
    "9. Does temperature meaningfully predict mobility demand?",
    q9_answer,
    q9_interpretation,
    q9_evidence,
    q9_calculation,
    q9_implication,
    q9_limitation,
)


# ----------------------------------------------------------------
# Q10 — Wind usefulness
# ----------------------------------------------------------------
q10_wind_corr = safe_corr(
    daily_weather,
    "max_wind_speed_mph",
    "total_trips",
)
if q10_wind_corr is not None:
    q10_answer = f"""
**No. Wind does not appear to be a meaningful standalone demand
driver in the current historical data.**

The Pearson correlation between maximum wind speed and daily trips is
**{q10_wind_corr:.3f}**, which is negligible.

The validated statistical analysis found **p = 0.475544**, meaning the
observed relationship is not statistically significant in the simple
pairwise test.
"""
else:
    q10_answer = """
The current weather dataset does not contain enough valid observations
to evaluate wind speed against daily demand.
"""

q10_interpretation = """
This is an important negative finding because a good BI product should
identify variables that do not provide strong evidence, not only
variables that appear interesting.

Wind speed has almost no linear relationship with daily taxi demand in
the current dataset. The statistical test also does not provide
sufficient evidence to treat the observed relationship as meaningful.

That does not prove that wind never matters. Extreme wind events could
behave differently from ordinary conditions, and nonlinear or
threshold effects could exist. It simply means that the available
historical observations do not support wind as a strong standalone
linear demand signal.
"""

q10_evidence = """
The validated statistical analysis used **365 daily observations**.

Wind speed versus daily trips:

- **Pearson r = -0.0375**
- **Pearson p = 0.475544**
- **Spearman rho = 0.0043**
- **Spearman p = 0.934942**
- simple regression **R² = 0.0014**

The evidence is consistently weak.
"""

q10_calculation = """
The dashboard measures:

**corr(`max_wind_speed_mph`, `total_trips`)**

The statistical analysis also evaluates the same relationship using
Spearman correlation and simple linear regression.
"""

q10_implication = """
Wind should not be treated as a primary demand signal in a simple
historical rule based on this dataset.

It can remain available as a predictor in a multivariate model,
because a variable can still contribute jointly even when its simple
pairwise relationship is weak.
"""

q10_limitation = """
The conclusion concerns the available historical range of wind speeds.
It does not establish that extreme wind events are operationally
irrelevant or that wind could never matter in another dataset.
"""

render_answer(
    "10. Does wind speed appear to be a meaningful demand driver?",
    q10_answer,
    q10_interpretation,
    q10_evidence,
    q10_calculation,
    q10_implication,
    q10_limitation,
)


# ----------------------------------------------------------------
# Q11 — Snow demand impact
# ----------------------------------------------------------------
q11_dry_trips = get_weather_value(
    weather_impact,
    "Dry",
    "avg_daily_trips",
)
q11_snow_trips = get_weather_value(
    weather_impact,
    "Snow",
    "avg_daily_trips",
)
q11_snow_change = get_weather_impact_pct(
    weather_impact,
    "Snow",
)

if (
    q11_dry_trips is not None
    and q11_snow_trips is not None
    and q11_snow_change is not None
):
    q11_difference = q11_snow_trips - q11_dry_trips
    q11_answer = f"""
Snow produces the largest observed weather-category reduction in
average daily taxi demand.

Dry days average approximately **{number(q11_dry_trips)} trips/day**,
while snow days average approximately **{number(q11_snow_trips)}
trips/day**.

That is approximately **{abs(q11_difference):,.0f} fewer trips per day**,
or about **{abs(q11_snow_change):.1f}% lower demand** than the dry-day
baseline.
"""
else:
    q11_difference = None
    q11_answer = """
The current weather-impact table does not contain enough information
to calculate the snow-versus-dry demand comparison.
"""

q11_interpretation = """
Snow is the clearest downside demand scenario in the current weather
categories.

The difference is materially larger than the rain comparison. This is
important because it demonstrates that the system does not respond to
all weather categories in the same way.

The statistical analysis reinforces the size of this difference. The
weather ANOVA finds an overall difference among weather categories,
and Tukey HSD identifies snow as significantly different from dry,
light precipitation, and rain.

This makes snow more than a visual outlier in the dashboard. It is a
historical operating state associated with a substantially lower level
of observed taxi activity.
"""

q11_evidence = f"""
Weather-category averages are:

**Dry: {number(q11_dry_trips or 0)} trips/day**

**Snow: {number(q11_snow_trips or 0)} trips/day**

**Change versus dry: {signed_pct(q11_snow_change or 0)}**

The validated Tukey HSD results also found:

- Dry vs Snow: **adjusted p = 0.0001**
- Light precipitation vs Snow: **adjusted p = 0.0002**
- Rain vs Snow: **adjusted p = 0.0046**

All three comparisons reject the null of equal category means.
"""

q11_calculation = """
The demand impact is calculated as:

**(Snow average daily trips − Dry average daily trips) / Dry average daily trips × 100**

The absolute trip difference is calculated separately by subtracting
the two category means.
"""

q11_implication = """
Snow should be treated as a distinct historical operating scenario in
demand planning rather than being grouped into a generic precipitation
flag.

The magnitude of the observed reduction makes snow relevant to fleet,
staffing, revenue, and capacity planning discussions.
"""

q11_limitation = """
The analysis is historical and observational. The result does not prove
that snow alone caused the entire decline. It also represents category
averages, which can hide the variation among individual snow days.
"""

render_answer(
    "11. How different is mobility demand during snow compared with dry weather?",
    q11_answer,
    q11_interpretation,
    q11_evidence,
    q11_calculation,
    q11_implication,
    q11_limitation,
)


# ----------------------------------------------------------------
# Q12 — Snow revenue impact
# ----------------------------------------------------------------
q12_dry_revenue = get_weather_value(
    revenue_weather,
    "Dry",
    "avg_daily_gross_customer_charges_usd",
)
q12_snow_revenue = get_weather_value(
    revenue_weather,
    "Snow",
    "avg_daily_gross_customer_charges_usd",
)

if q12_dry_revenue is not None and q12_snow_revenue is not None:
    q12_revenue_difference = q12_snow_revenue - q12_dry_revenue
    q12_revenue_pct = (
        q12_revenue_difference / q12_dry_revenue * 100
        if q12_dry_revenue
        else 0
    )
    q12_answer = f"""
Snow days are associated with a substantial decline in average daily
gross customer charges.

Dry days average approximately **{money_precise(q12_dry_revenue)}** in
gross customer charges, compared with approximately
**{money_precise(q12_snow_revenue)}** on snow days.

That is a difference of approximately **{money_precise(q12_revenue_difference)}
per day**, equivalent to about **{abs(q12_revenue_pct):.2f}% lower**
revenue than the dry-day baseline.
"""
else:
    q12_revenue_difference = None
    q12_revenue_pct = None
    q12_answer = """
The current weather-revenue table does not contain enough information
to calculate the snow-versus-dry revenue comparison.
"""

q12_interpretation = """
The revenue result translates the demand effect into a financial
operating signal.

The observed snow-day reduction is larger than the corresponding rain
reduction. That makes snow particularly relevant for historical
financial scenario planning.

The important point is that the dashboard is measuring gross customer
charges, not profit. A decline in gross charges indicates lower observed
customer spending associated with the weather category, but it does
not tell us how operating costs, driver compensation, or margins moved.

Even with that limitation, the result is operationally useful because
revenue expectations should not necessarily assume that every day has
the same historical financial profile.
"""

q12_evidence = f"""
**Dry average daily gross customer charges: {money_precise(q12_dry_revenue or 0)}**

**Snow average daily gross customer charges: {money_precise(q12_snow_revenue or 0)}**

**Difference: {money_precise(q12_revenue_difference or 0)} per day**

**Relative change: {pct(q12_revenue_pct or 0)}**

The validated statistical analysis reports the snow-day average as
approximately **$53,262.51**, compared with **$68,931.46** for dry days.
"""

q12_calculation = """
The dollar difference is:

**Snow daily revenue − Dry daily revenue**

The percentage difference is:

**(Snow daily revenue − Dry daily revenue) / Dry daily revenue × 100**
"""

q12_implication = """
Historical snow conditions can be used as a downside revenue scenario
for planning discussions.

The result is particularly useful when presented alongside the snow
demand reduction, because management can see that the weather signal
appears in both operating volume and gross customer charges.
"""

q12_limitation = """
This is gross customer charge data, not net revenue or profit. The
historical association should not be used as a forecast for a specific
future snowstorm.
"""

render_answer(
    "12. How much revenue exposure is associated with snow?",
    q12_answer,
    q12_interpretation,
    q12_evidence,
    q12_calculation,
    q12_implication,
    q12_limitation,
)


# ----------------------------------------------------------------
# Q13 — Rain revenue impact
# ----------------------------------------------------------------
q13_dry_revenue = get_weather_value(
    revenue_weather,
    "Dry",
    "avg_daily_gross_customer_charges_usd",
)
q13_rain_revenue = get_weather_value(
    revenue_weather,
    "Rain",
    "avg_daily_gross_customer_charges_usd",
)

if q13_dry_revenue is not None and q13_rain_revenue is not None:
    q13_revenue_difference = q13_rain_revenue - q13_dry_revenue
    q13_revenue_pct = (
        q13_revenue_difference / q13_dry_revenue * 100
        if q13_dry_revenue
        else 0
    )
    q13_answer = f"""
Rain days are associated with a more moderate revenue decline than
snow days.

Dry days average approximately **{money_precise(q13_dry_revenue)}** in
gross customer charges, while rain days average approximately
**{money_precise(q13_rain_revenue)}**.

That is approximately **{money_precise(q13_revenue_difference)} per day**,
or about **{abs(q13_revenue_pct):.2f}% lower** than the dry-day baseline.
"""
else:
    q13_revenue_difference = None
    q13_revenue_pct = None
    q13_answer = """
The current weather-revenue table does not contain enough information
to calculate the rain-versus-dry revenue comparison.
"""

q13_interpretation = """
Rain produces a measurable financial difference, but the effect is
considerably smaller than the snow effect.

That distinction is important for operational planning. A generic
"bad weather" rule would treat rain and snow as equivalent conditions,
while the historical data shows that they represent different business
environments.

The rain result should therefore be interpreted as a moderate
historical revenue exposure rather than as a catastrophic demand event.
It also provides a financial complement to the demand result: rain
reduces average daily trips relative to dry conditions, and average
daily gross customer charges move in the same direction.
"""

q13_evidence = f"""
**Dry average daily gross customer charges: {money_precise(q13_dry_revenue or 0)}**

**Rain average daily gross customer charges: {money_precise(q13_rain_revenue or 0)}**

**Difference: {money_precise(q13_revenue_difference or 0)} per day**

**Relative change: {pct(q13_revenue_pct or 0)}**

The validated analysis reports approximately **$68,931.46** for dry
days and **$65,942.37** for rain days.
"""

q13_calculation = """
The dashboard compares the average daily gross customer charges for
rain and dry conditions.

**Rain revenue impact = (Rain revenue − Dry revenue) / Dry revenue × 100**

The dollar difference is retained so management can see both the
relative and absolute magnitude.
"""

q13_implication = """
Rain can be incorporated into historical financial scenario planning,
but it should not trigger the same assumptions used for snow.

A graduated weather-response framework is therefore more defensible:
normal dry conditions, light precipitation, rain, and snow should be
considered separately when the data supports them.
"""

q13_limitation = """
The result is an historical category comparison. It does not establish
causation and does not include costs, profitability, refunds, or other
financial variables required for a full financial impact model.
"""

render_answer(
    "13. How much revenue is associated with rainy conditions compared with dry conditions?",
    q13_answer,
    q13_interpretation,
    q13_evidence,
    q13_calculation,
    q13_implication,
    q13_limitation,
)


# ----------------------------------------------------------------
# Q14 — Confidence interval around daily demand
# ----------------------------------------------------------------
q14_mean = safe_mean(daily_weather, "total_trips")
q14_values = pd.Series(dtype="float64")
if daily_weather is not None and not daily_weather.empty and "total_trips" in daily_weather.columns:
    q14_values = pd.to_numeric(
        daily_weather["total_trips"], errors="coerce"
    ).dropna()

if len(q14_values) >= 2:
    q14_n = len(q14_values)
    q14_std = float(q14_values.std(ddof=1))
    q14_se = q14_std / math.sqrt(q14_n)
    # A t critical value is used when SciPy is available. The fallback
    # keeps the dashboard functional even if an optional statistical
    # dependency is unavailable.
    try:
        from scipy import stats
        q14_t_critical = float(stats.t.ppf(0.975, q14_n - 1))
    except Exception:
        q14_t_critical = 1.96
    q14_margin = q14_t_critical * q14_se
    q14_lower = q14_mean - q14_margin
    q14_upper = q14_mean + q14_margin

    q14_answer = f"""
The estimated mean daily demand is **{number(q14_mean)} trips per day**.

Using the {q14_n} daily observations, the approximate **95% confidence
interval is {number(q14_lower)} to {number(q14_upper)} trips per day**.

In practical terms, the historical sample supports a relatively tight
range around the estimated average daily demand.
"""
else:
    q14_n = 0
    q14_lower = None
    q14_upper = None
    q14_answer = """
The current daily dataset does not contain enough valid observations
to calculate a 95% confidence interval for average daily demand.
"""

q14_interpretation = """
A confidence interval adds statistical context to the dashboard's
average-demand benchmark.

The mean alone is a point estimate. The interval communicates how much
uncertainty surrounds that estimate given the available daily sample.

The current interval is relatively narrow compared with the daily mean,
which means the estimate of the historical average is reasonably precise
for this dataset.

This should not be interpreted as a prediction interval for the next
day. A confidence interval around the mean answers a different question:
it describes uncertainty around the estimated average level of the
historical population represented by the sample.
"""

q14_evidence = f"""
The calculation uses **{q14_n} valid daily observations** from the
`total_trips` field.

**Mean daily trips: {number(q14_mean)}**

**95% CI lower bound: {number(q14_lower or 0)}**

**95% CI upper bound: {number(q14_upper or 0)}**

The validated statistical analysis independently reported approximately
**2,720 to 2,852 trips/day** for the 95% confidence interval.
"""

q14_calculation = """
The interval is calculated as:

**mean ± t-critical × (sample standard deviation / √n)**

with a 95% confidence level and `n` equal to the number of valid daily
observations.
"""

q14_implication = """
The interval provides management with a statistically grounded baseline
rather than presenting the daily average as an exact constant.

It is useful when communicating historical demand to decision-makers
who need to distinguish an estimated normal level from an exact,
unchanging operating requirement.
"""

q14_limitation = """
A confidence interval around the mean is not a forecast interval for a
future day. Individual days can fall far outside the interval because
weather, seasonality, weekday effects, and other factors create daily
variation.
"""

render_answer(
    "14. How confident are we about the system's typical daily demand?",
    q14_answer,
    q14_interpretation,
    q14_evidence,
    q14_calculation,
    q14_implication,
    q14_limitation,
)


# ----------------------------------------------------------------
# Q15 — Overall weather-category difference
# ----------------------------------------------------------------
q15_groups = []
q15_group_counts = {}
if (
    daily_weather is not None
    and not daily_weather.empty
    and "weather_condition" in daily_weather.columns
    and "total_trips" in daily_weather.columns
):
    q15_working = daily_weather[["weather_condition", "total_trips"]].copy()
    q15_working["total_trips"] = pd.to_numeric(
        q15_working["total_trips"], errors="coerce"
    )
    q15_working = q15_working.dropna(subset=["weather_condition", "total_trips"])
    for condition, group in q15_working.groupby("weather_condition"):
        values = group["total_trips"].dropna().tolist()
        if len(values) >= 2:
            q15_groups.append(values)
            q15_group_counts[str(condition)] = len(values)

q15_f = None
q15_p = None
if len(q15_groups) >= 2:
    try:
        from scipy import stats
        q15_f, q15_p = stats.f_oneway(*q15_groups)
        q15_f = float(q15_f)
        q15_p = float(q15_p)
    except Exception:
        q15_f = None
        q15_p = None

if q15_p is not None:
    if q15_p < 0.001:
        q15_significance = "highly statistically significant"
    elif q15_p < 0.05:
        q15_significance = "statistically significant"
    else:
        q15_significance = "not statistically significant"

    q15_answer = f"""
**Yes. The observed weather categories are not all associated with the
same average level of daily taxi demand.**

The one-way ANOVA produces an **F-statistic of {q15_f:.4f}** with a
**p-value of {q15_p:.6f}**, indicating a **{q15_significance}** overall
difference among the weather-category means.

The important business point is that weather should not be reduced to
a single yes/no precipitation flag. The category matters.
"""
else:
    q15_answer = """
The current daily weather data does not contain enough valid weather
categories to calculate an overall ANOVA comparison.
"""

q15_interpretation = """
This is the dashboard's broadest weather-demand question.

Individual comparisons can show that snow differs from dry conditions,
but an overall test asks a more fundamental question: do the weather
categories as a group appear to have the same average demand, or is
there evidence that at least one category differs?

The answer is that the category means are statistically different in
the historical data. The follow-up Tukey HSD analysis identifies the
specific differences, with snow differing significantly from dry, light
precipitation, and rain.

This supports a graduated weather framework rather than a generic
"bad-weather" indicator. Dry, light precipitation, rain, and snow should
be preserved as distinct historical states when the dashboard evaluates
scenario differences.
"""

q15_evidence = f"""
The dashboard groups daily `total_trips` by `weather_condition` and
runs a one-way ANOVA across the available categories.

Observed groups in the current data include:

{', '.join(f'**{name} ({count} days)**' for name, count in q15_group_counts.items())}

Validated statistical-analysis results:

- **F-statistic = 6.9232**
- **p-value = 0.000153**
- **Eta-squared = 0.0544**

The Tukey HSD follow-up found significant differences for Dry vs Snow,
Light precipitation vs Snow, and Rain vs Snow.
"""

q15_calculation = """
The overall test is a one-way ANOVA comparing the mean `total_trips`
values across weather categories.

The null hypothesis is:

**All weather-category means are equal.**

A small p-value provides evidence against that null hypothesis. Tukey
HSD is then used to identify which specific pairs differ after the
overall test.
"""

q15_implication = """
The finding supports a more sophisticated operational weather strategy.

Instead of a binary rule such as:

**NORMAL → BAD WEATHER**

the historical evidence supports a graduated framework:

**DRY → LIGHT PRECIPITATION → RAIN → SNOW**

Each state can be associated with its own historical demand and revenue
benchmarks. That structure can later become an input to a forecasting or
scenario-planning model.
"""

q15_limitation = """
ANOVA establishes that at least one group differs; it does not establish
that weather caused the difference. The category averages can also
reflect other factors that happen to occur during the same days.

The result should therefore be combined with effect size, regression,
correlation, and operational context rather than interpreted alone.
"""

render_answer(
    "15. Does weather meaningfully separate different demand environments?",
    q15_answer,
    q15_interpretation,
    q15_evidence,
    q15_calculation,
    q15_implication,
    q15_limitation,
)


st.divider()


st.header(
    "📈 Weather Evidence"
)

st.markdown(
    """
    The questions above are easier to understand when the
    underlying weather categories are visible together.

    This section provides the supporting visual evidence
    without replacing the question-and-answer structure.
    """
)


if (
    weather_impact is not None
    and not weather_impact.empty
):
    weather_chart_data = weather_impact.copy()

    if "avg_daily_trips" in weather_chart_data.columns:
        weather_chart_data[
            "avg_daily_trips"
        ] = pd.to_numeric(
            weather_chart_data[
                "avg_daily_trips"
            ],
            errors="coerce",
        )

    weather_chart_data = weather_chart_data.dropna(
        subset=["avg_daily_trips"]
    )

    if not weather_chart_data.empty:
        fig_weather = px.bar(
            weather_chart_data.sort_values(
                "avg_daily_trips"
            ),
            x="avg_daily_trips",
            y="weather_condition",
            orientation="h",
            title="Average Daily Taxi Demand by Weather Condition",
            labels={
                "avg_daily_trips":
                    "Average daily trips",
                "weather_condition":
                    "Weather condition",
            },
            hover_data=[
                column
                for column in [
                    "days_in_category",
                    "avg_daily_gross_charges_usd",
                    "avg_daily_tips_usd",
                ]
                if column in weather_chart_data.columns
            ],
        )

        st.plotly_chart(
            fig_weather,
            use_container_width=True,
        )


if (
    revenue_weather is not None
    and not revenue_weather.empty
):
    revenue_chart_data = revenue_weather.copy()

    if (
        "avg_daily_gross_customer_charges_usd"
        in revenue_chart_data.columns
    ):
        revenue_chart_data[
            "avg_daily_gross_customer_charges_usd"
        ] = pd.to_numeric(
            revenue_chart_data[
                "avg_daily_gross_customer_charges_usd"
            ],
            errors="coerce",
        )

        revenue_chart_data = revenue_chart_data.dropna(
            subset=[
                "avg_daily_gross_customer_charges_usd"
            ]
        )

        if not revenue_chart_data.empty:
            fig_revenue = px.bar(
                revenue_chart_data.sort_values(
                    "avg_daily_gross_customer_charges_usd"
                ),
                x=(
                    "avg_daily_gross_customer_charges_usd"
                ),
                y="weather_condition",
                orientation="h",
                title=(
                    "Average Daily Gross Customer Charges "
                    "by Weather Condition"
                ),
                labels={
                    "avg_daily_gross_customer_charges_usd":
                        "Average daily gross charges (USD)",
                    "weather_condition":
                        "Weather condition",
                },
            )

            st.plotly_chart(
                fig_revenue,
                use_container_width=True,
            )


st.divider()


st.header(
    "🌡️ Temperature and Demand"
)

st.markdown(
    """
    The temperature analysis provides a second way to
    understand environmental exposure.

    Weather categories are discrete labels.

    Temperature is continuous.

    Looking at the continuous variable allows the dashboard
    to investigate whether demand changes progressively as
    temperature changes or whether the relationship appears
    more irregular.
    """
)


if (
    daily_weather is not None
    and not daily_weather.empty
    and "avg_temperature_f" in daily_weather.columns
    and "total_trips" in daily_weather.columns
):
    temperature_plot = daily_weather.copy()

    temperature_plot[
        "avg_temperature_f"
    ] = pd.to_numeric(
        temperature_plot[
            "avg_temperature_f"
        ],
        errors="coerce",
    )

    temperature_plot[
        "total_trips"
    ] = pd.to_numeric(
        temperature_plot[
            "total_trips"
        ],
        errors="coerce",
    )

    temperature_plot = temperature_plot.dropna(
        subset=[
            "avg_temperature_f",
            "total_trips",
        ]
    )

    if not temperature_plot.empty:
        fig_temperature = px.scatter(
            temperature_plot,
            x="avg_temperature_f",
            y="total_trips",
            color=(
                "weather_condition"
                if "weather_condition"
                in temperature_plot.columns
                else None
            ),
            trendline="ols",
            title=(
                "Daily Average Temperature vs Taxi Demand"
            ),
            labels={
                "avg_temperature_f":
                    "Average temperature (°F)",
                "total_trips":
                    "Daily taxi trips",
                "weather_condition":
                    "Weather condition",
            },
            hover_data=[
                column
                for column in [
                    "trip_date",
                    "precipitation_inches",
                    "snowfall_inches",
                    "max_wind_speed_mph",
                ]
                if column in temperature_plot.columns
            ],
        )

        st.plotly_chart(
            fig_temperature,
            use_container_width=True,
        )


st.divider()


st.header(
    "📅 Weather × Weekday"
)

st.markdown(
    """
    Weather should not be interpreted independently of the
    weekly demand cycle.

    This section exposes the weekday-weather relationship
    that supports Question 13.

    The purpose is not simply to create another chart.

    The purpose is to show why a weather response should be
    interpreted within the normal operating pattern of the
    day.
    """
)


if (
    weekday_weather is not None
    and not weekday_weather.empty
):
    weekday_weather_plot = weekday_weather.copy()

    if "avg_daily_trips" in weekday_weather_plot.columns:
        weekday_weather_plot[
            "avg_daily_trips"
        ] = pd.to_numeric(
            weekday_weather_plot[
                "avg_daily_trips"
            ],
            errors="coerce",
        )

    weekday_weather_plot = weekday_weather_plot.dropna(
        subset=["avg_daily_trips"]
    )

    if not weekday_weather_plot.empty:
        fig_weekday_weather = px.bar(
            weekday_weather_plot,
            x="day_of_week",
            y="avg_daily_trips",
            color="weather_condition",
            barmode="group",
            title=(
                "Average Taxi Demand by Weekday and "
                "Weather Condition"
            ),
            labels={
                "day_of_week":
                    "Day of week",
                "avg_daily_trips":
                    "Average daily trips",
                "weather_condition":
                    "Weather condition",
            },
        )

        st.plotly_chart(
            fig_weekday_weather,
            use_container_width=True,
        )


st.divider()


st.header(
    "💵 Weather × Revenue"
)

st.markdown(
    """
    The revenue view connects the operational demand
    findings to financial performance.

    A reduction in trips does not automatically imply the
    same proportional reduction in gross customer charges.

    Looking at daily revenue and revenue per trip allows the
    dashboard to separate those effects.
    """
)


if (
    revenue_weather is not None
    and not revenue_weather.empty
):
    revenue_columns = [
        column
        for column in [
            "weather_condition",
            "days_in_category",
            "avg_daily_trips",
            "avg_daily_gross_customer_charges_usd",
            "avg_daily_tips_usd",
            "avg_customer_charge_per_trip_usd",
        ]
        if column in revenue_weather.columns
    ]

    if revenue_columns:
        display_revenue = revenue_weather[
            revenue_columns
        ].copy()

        st.dataframe(
            display_revenue,
            use_container_width=True,
            hide_index=True,
        )


st.divider()


st.header(
    "🗺️ Spatial Ground-Truth"
)

st.markdown(
    """
    The current spatial capability is intentionally narrow.

    We can identify where taxi demand is concentrated because
    the warehouse contains pickup-zone information.

    We cannot currently claim which pickup zones receive the
    most rain.

    The weather source is city-level.

    Therefore, the valid spatial question is:

    **Where is taxi demand concentrated?**

    The invalid question would be:

    **Which neighborhood receives the most rain?**

    That distinction protects the dashboard from creating a
    spatial conclusion that the data does not support.
    """
)


if (
    pickup_zones is not None
    and not pickup_zones.empty
):
    spatial_data = pickup_zones.copy()

    if "total_trips" in spatial_data.columns:
        spatial_data[
            "total_trips"
        ] = pd.to_numeric(
            spatial_data[
                "total_trips"
            ],
            errors="coerce",
        )

        spatial_data = spatial_data.dropna(
            subset=["total_trips"]
        )

        spatial_data = spatial_data.sort_values(
            "total_trips",
            ascending=False,
        )

        top_spatial = spatial_data.head(
            15
        ).copy()

        top_spatial = top_spatial.sort_values(
            "total_trips"
        )

        fig_zones = px.bar(
            top_spatial,
            x="total_trips",
            y="pickup_zone",
            orientation="h",
            title="Top Pickup Zones by Annual Taxi Trips",
            labels={
                "total_trips":
                    "Total trips",
                "pickup_zone":
                    "Pickup zone",
            },
            hover_data=[
                column
                for column in [
                    "borough",
                    "avg_trip_distance_miles",
                ]
                if column in top_spatial.columns
            ],
        )

        st.plotly_chart(
            fig_zones,
            use_container_width=True,
        )


st.divider()


st.header(
    "❄️ Historical Weather Scenario Simulator"
)

st.markdown(
    """
    The scenario simulator does not pretend to predict the
    future.

    Instead, it asks:

    "If we use a historical weather category as the scenario,
    what was the observed average daily demand?"

    This distinction is important.

    A historical scenario is descriptive.

    A predictive forecast requires a model trained to predict
    future observations.
    """
)


if (
    weather_impact is not None
    and not weather_impact.empty
    and "weather_condition"
    in weather_impact.columns
):
    scenario_options = (
        weather_impact[
            "weather_condition"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if scenario_options:
        selected_weather = st.selectbox(
            "Choose a historical weather scenario",
            scenario_options,
        )

        selected_demand = get_weather_value(
            weather_impact,
            selected_weather,
            "avg_daily_trips",
        )

        baseline_demand = get_weather_value(
            weather_impact,
            "Dry",
            "avg_daily_trips",
        )

        if (
            selected_demand is not None
            and baseline_demand is not None
        ):
            demand_difference = (
                selected_demand
                - baseline_demand
            )

            demand_change_pct = (
                demand_difference
                / baseline_demand
                * 100
                if baseline_demand
                else 0
            )

            scenario_col1, scenario_col2, scenario_col3 = (
                st.columns(3)
            )

            with scenario_col1:
                st.metric(
                    "Dry-day baseline",
                    number(baseline_demand),
                    "trips/day",
                )

            with scenario_col2:
                st.metric(
                    f"{selected_weather} scenario",
                    number(selected_demand),
                    "trips/day",
                )

            with scenario_col3:
                st.metric(
                    "Difference from dry",
                    signed_number(
                        demand_difference
                    ),
                    signed_pct(
                        demand_change_pct
                    ),
                )


st.divider()


st.header(
    "📋 Current Analytical Coverage"
)

coverage = pd.DataFrame(
    {
        "Capability": [
            "Taxi trip demand",
            "Average daily demand",
            "Hourly demand",
            "Monthly demand",
            "Weekday demand",
            "Pickup-zone demand",
            "Daily weather",
            "Temperature",
            "Precipitation",
            "Snowfall",
            "Wind",
            "Weather × weekday",
            "Weather × revenue",
            "Gross customer charges",
            "Customer tips",
            "Average charge per trip",
            "Real-time GPS",
            "Public transit telemetry",
            "Transit delays",
            "Micro-mobility trips",
            "Dock availability",
            "EV fleet telemetry",
            "EV battery state of charge",
            "Weather radar",
            "Real-time incidents",
            "Future climate projections",
        ],
        "Status": [
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
        ],
        "Used by BI Questions": [
            "Yes",
            "Yes",
            "Supporting data",
            "Supporting data",
            "Supporting data",
            "Supporting data",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "Yes",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
        ],
    }
)

st.dataframe(
    coverage,
    use_container_width=True,
    hide_index=True,
)


st.divider()


st.header(
    "🎯 BI Decision Summary"
)

st.markdown(
    """
    ## What the current data tells us

    The historical dataset supports a clear set of
    operational and financial observations.

    Taxi demand is measurable at a citywide daily level.

    Weather conditions are associated with different levels
    of demand.

    Rain produces a lower average daily demand than dry
    conditions.

    Light precipitation does not behave like rain.

    Revenue changes alongside the demand environment.

    Customer tips also change across weather conditions.

    Average customer charge per trip provides an additional
    dimension beyond total trip volume.

    Weather effects can vary by weekday.

    Temperature can be tested as a continuous explanatory
    variable.

    Pickup zones reveal where taxi activity is concentrated.

    These findings create a defensible historical BI layer.
    """
)

st.markdown(
    """
    ## What the current data does not tell us

    The current model does not provide real-time information
    about:

    - traffic congestion
    - transit delays
    - subway crowding
    - bus route performance
    - bike availability
    - scooter availability
    - EV battery state
    - charging stations
    - live vehicle locations
    - current flooded intersections
    - real-time incidents
    - weather radar
    - future climate scenarios

    Those are not weaknesses in the BI page.

    They are boundaries around what can responsibly be
    claimed from the current warehouse.

    A professional analytics product should expose those
    boundaries rather than silently inventing data.
    """
)

st.markdown(
    """
    ## The business value of this layer

    The value of the BI page is not simply that it contains
    charts.

    Its value is that each chart is connected to a business
    question.

    The question defines the metric.

    The metric defines the calculation.

    The calculation produces the answer.

    The answer produces the interpretation.

    The interpretation leads to a potential decision.

    That structure makes the dashboard easier to defend in
    a technical interview because the analysis can be traced
    from the business question back to the underlying data.
    """
)

st.markdown(
    """
    ## The analytical progression

    The current project follows a deliberate progression.

    **First: establish demand.**

    How many trips are represented?

    What does a normal day look like?

    **Second: establish financial performance.**

    What does a typical day generate in gross customer
    charges?

    What happens to tips?

    What happens to charge per trip?

    **Third: test weather exposure.**

    Does rain change demand?

    Does light precipitation behave differently?

    Does weather change revenue?

    **Fourth: introduce interaction effects.**

    Does weather behave differently across weekdays?

    **Fifth: test continuous environmental variables.**

    Is temperature associated with demand?

    **Sixth: preserve spatial intelligence.**

    Where is taxi demand concentrated?

    **Seventh: translate historical observations into
    scenarios.**

    What does observed demand look like under different
    historical weather conditions?

    This creates a coherent BI workflow instead of a
    collection of disconnected visualizations.
    """
)


st.divider()


st.caption(
    "Urban Mobility Analytics • BigQuery • Python • Streamlit • Plotly"
)

st.caption(
    "Business Intelligence and Decision Support Layer • Historical 2021 Analysis"
)