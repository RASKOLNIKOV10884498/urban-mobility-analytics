"""Weather and geographic analysis for Urban Mobility Analytics."""

from __future__ import annotations

import streamlit as st

from data_loader import (
    load_daily_weather,
    load_pickup_zones,
    load_precipitation_impact,
    load_snowfall_impact,
    load_temperature_impact,
    load_weather_impact,
    load_weekday_weather_impact,
    load_wind_impact,
)

from charts import (
    pickup_zone_chart,
    precipitation_impact_chart,
    snowfall_impact_chart,
    temperature_demand_chart,
    temperature_impact_chart,
    weather_demand_chart,
    weekday_weather_chart,
    wind_impact_chart,
)

from metrics import (
    get_top_pickup_zone,
    get_weather_comparison,
    get_weather_extremes,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Weather & Geography",
    page_icon="🌦️",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🌦️ Weather & Geography Intelligence")

st.markdown(
    """
    Analyze how **weather conditions and pickup-zone activity**
    affect urban taxi demand throughout 2021.
    """
)


# ============================================================
# LOAD DATA
# ============================================================

daily_weather = load_daily_weather()
weather_impact = load_weather_impact()
temperature_impact = load_temperature_impact()
precipitation_impact = load_precipitation_impact()
snowfall_impact = load_snowfall_impact()
wind_impact = load_wind_impact()
weekday_weather = load_weekday_weather_impact()
pickup_zones = load_pickup_zones()


# ============================================================
# WEATHER OVERVIEW
# ============================================================

st.divider()

st.subheader("🌦️ Weather Demand Overview")

highest_weather, lowest_weather = get_weather_extremes(
    weather_impact
)

col1, col2, col3, col4 = st.columns(4)


# ------------------------------------------------------------
# Highest-demand weather
# ------------------------------------------------------------

with col1:

    if not highest_weather.empty:

        weather_name = highest_weather.get(
            "weather_condition",
            "N/A",
        )

        demand = highest_weather.get(
            "avg_daily_trips",
            0,
        )

        st.metric(
            "Highest Demand Weather",
            str(weather_name),
            f"{float(demand):,.0f} trips/day",
        )

    else:

        st.metric(
            "Highest Demand Weather",
            "N/A",
        )


# ------------------------------------------------------------
# Lowest-demand weather
# ------------------------------------------------------------

with col2:

    if not lowest_weather.empty:

        weather_name = lowest_weather.get(
            "weather_condition",
            "N/A",
        )

        demand = lowest_weather.get(
            "avg_daily_trips",
            0,
        )

        st.metric(
            "Lowest Demand Weather",
            str(weather_name),
            f"{float(demand):,.0f} trips/day",
        )

    else:

        st.metric(
            "Lowest Demand Weather",
            "N/A",
        )


# ------------------------------------------------------------
# Top pickup zone
# ------------------------------------------------------------

with col3:

    top_zone = get_top_pickup_zone(
        pickup_zones
    )

    if not top_zone.empty:

        zone_name = top_zone.get(
            "pickup_zone",
            "N/A",
        )

        trips = top_zone.get(
            "total_trips",
            0,
        )

        st.metric(
            "Top Pickup Zone",
            str(zone_name),
            f"{float(trips):,.0f} trips",
        )

    else:

        st.metric(
            "Top Pickup Zone",
            "N/A",
        )


# ------------------------------------------------------------
# Weather records
# ------------------------------------------------------------

with col4:

    weather_days = (
        len(daily_weather)
        if daily_weather is not None
        else 0
    )

    st.metric(
        "Weather Records",
        f"{weather_days:,}",
        "Daily observations",
    )


# ============================================================
# WEATHER CONDITION DEMAND
# ============================================================

st.divider()

st.subheader("🌧️ Demand by Weather Condition")

if weather_impact.empty:

    st.warning(
        "No weather-impact data is available."
    )

else:

    st.plotly_chart(
        weather_demand_chart(weather_impact),
        use_container_width=True,
    )


# ============================================================
# WEATHER COMPARISON TABLE
# ============================================================

st.subheader("📊 Weather Demand Comparison")

weather_comparison = get_weather_comparison(
    weather_impact
)

if not weather_comparison.empty:

    display_columns = [
        column
        for column in [
            "weather_condition",
            "days_in_category",
            "avg_daily_trips",
            "vs_dry_pct",
        ]
        if column in weather_comparison.columns
    ]

    display_data = weather_comparison[
        display_columns
    ].copy()

    if "avg_daily_trips" in display_data.columns:
        display_data[
            "avg_daily_trips"
        ] = display_data[
            "avg_daily_trips"
        ].round(0)

    if "vs_dry_pct" in display_data.columns:
        display_data[
            "vs_dry_pct"
        ] = display_data[
            "vs_dry_pct"
        ].round(1)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# TEMPERATURE ANALYSIS
# ============================================================

st.divider()

st.subheader("🌡️ Temperature Impact")

col1, col2 = st.columns(2)


with col1:

    if temperature_impact.empty:

        st.warning(
            "No temperature-band data is available."
        )

    else:

        st.plotly_chart(
            temperature_impact_chart(
                temperature_impact
            ),
            use_container_width=True,
        )


with col2:

    if daily_weather.empty:

        st.warning(
            "No daily weather-demand data is available."
        )

    else:

        st.plotly_chart(
            temperature_demand_chart(
                daily_weather
            ),
            use_container_width=True,
        )


# ============================================================
# PRECIPITATION AND SNOWFALL
# ============================================================

st.divider()

st.subheader("🌧️ Precipitation & Snowfall")

col1, col2 = st.columns(2)


with col1:

    if precipitation_impact.empty:

        st.warning(
            "No precipitation-impact data is available."
        )

    else:

        st.plotly_chart(
            precipitation_impact_chart(
                precipitation_impact
            ),
            use_container_width=True,
        )


with col2:

    if snowfall_impact.empty:

        st.warning(
            "No snowfall-impact data is available."
        )

    else:

        st.plotly_chart(
            snowfall_impact_chart(
                snowfall_impact
            ),
            use_container_width=True,
        )


# ============================================================
# WIND ANALYSIS
# ============================================================

st.divider()

st.subheader("💨 Wind Impact")

if wind_impact.empty:

    st.warning(
        "No wind-impact data is available."
    )

else:

    st.plotly_chart(
        wind_impact_chart(wind_impact),
        use_container_width=True,
    )


# ============================================================
# WEATHER × WEEKDAY
# ============================================================

st.divider()

st.subheader("📅 Weather × Weekday Demand")

if weekday_weather.empty:

    st.warning(
        "No weekday-weather data is available."
    )

else:

    st.plotly_chart(
        weekday_weather_chart(
            weekday_weather
        ),
        use_container_width=True,
    )


# ============================================================
# PICKUP-ZONE ANALYSIS
# ============================================================

st.divider()

st.subheader("🗺️ Pickup-Zone Activity")

st.markdown(
    """
    Geographic analysis is based on **pickup-zone activity**.
    Coordinates are intentionally not required for this project.
    """
)

if pickup_zones.empty:

    st.warning(
        "No pickup-zone data is available."
    )

else:

    st.plotly_chart(
        pickup_zone_chart(pickup_zones),
        use_container_width=True,
    )


# ============================================================
# TOP PICKUP ZONES TABLE
# ============================================================

st.subheader("🏆 Highest-Volume Pickup Zones")

if not pickup_zones.empty:

    top_zones = pickup_zones.copy()

    if "total_trips" in top_zones.columns:

        top_zones = (
            top_zones
            .sort_values(
                "total_trips",
                ascending=False,
            )
            .head(15)
        )

    display_columns = [
        column
        for column in [
            "borough",
            "pickup_zone",
            "total_trips",
            "avg_trip_distance_miles",
        ]
        if column in top_zones.columns
    ]

    st.dataframe(
        top_zones[display_columns],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# DAILY WEATHER DATA
# ============================================================

st.divider()

st.subheader("📋 Daily Weather & Demand Data")

if daily_weather.empty:

    st.warning(
        "No daily weather data is available."
    )

else:

    st.dataframe(
        daily_weather,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Weather source: Open-Meteo historical API • "
    "Mobility source: BigQuery analytical datasets • "
    "Historical period: 2021"
)