"""Cached BigQuery data-loading functions for Urban Mobility Analytics."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from bigquery import load_analytics_table


CACHE_TTL = 600


# ============================================================
# MOBILITY DATA
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def load_monthly_trips() -> pd.DataFrame:
    """Load monthly trip demand."""
    return load_analytics_table("monthly_trip_summary_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_hourly_trips() -> pd.DataFrame:
    """Load hourly trip demand."""
    return load_analytics_table("hourly_trip_summary_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_weekday_trips() -> pd.DataFrame:
    """Load weekday trip demand."""
    return load_analytics_table("weekday_trip_summary_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_pickup_zones() -> pd.DataFrame:
    """Load pickup-zone trip demand."""
    return load_analytics_table("pickup_zone_summary_2021")


# ============================================================
# WEATHER DATA
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def load_daily_weather() -> pd.DataFrame:
    """
    Load the 365-day daily mobility and weather dataset.

    Columns currently available:
        trip_date
        total_trips
        avg_trip_distance_miles
        avg_temperature_f
        max_temperature_f
        precipitation_inches
        snowfall_inches
        max_wind_speed_mph
        weather_code
        weather_condition
    """
    return load_analytics_table("weather_demand_daily_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_weather_impact() -> pd.DataFrame:
    """Load demand aggregated by weather condition."""
    return load_analytics_table("weather_impact_summary_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_temperature_impact() -> pd.DataFrame:
    """Load demand and revenue by temperature band."""
    return load_analytics_table("temperature_impact_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_precipitation_impact() -> pd.DataFrame:
    """Load demand and revenue by precipitation band."""
    return load_analytics_table("precipitation_impact_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_snowfall_impact() -> pd.DataFrame:
    """Load demand and revenue by snowfall band."""
    return load_analytics_table("snowfall_impact_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_wind_impact() -> pd.DataFrame:
    """Load demand and revenue by wind-speed band."""
    return load_analytics_table("wind_impact_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_weekday_weather_impact() -> pd.DataFrame:
    """Load weather impact broken down by weekday."""
    return load_analytics_table("weekday_weather_impact_2021")


# ============================================================
# REVENUE DATA
# ============================================================

@st.cache_data(ttl=CACHE_TTL)
def load_revenue_weather_daily() -> pd.DataFrame:
    """
    Load daily taxi revenue and weather data.

    This table is separate from weather_demand_daily_2021
    because it contains the financial metrics needed for
    revenue analysis.
    """
    return load_analytics_table("taxi_revenue_weather_daily_2021")


@st.cache_data(ttl=CACHE_TTL)
def load_revenue_weather_impact() -> pd.DataFrame:
    """
    Load revenue aggregated by weather condition.

    Current columns include:
        weather_condition
        days_in_category
        total_gross_customer_charges_usd
        avg_daily_gross_customer_charges_usd
        avg_daily_tips_usd
        avg_customer_charge_per_trip_usd
        avg_daily_trips
    """
    return load_analytics_table("taxi_revenue_weather_impact_2021")


# ============================================================
# BACKWARD-COMPATIBLE ALIASES
# ============================================================

load_monthly_data = load_monthly_trips
load_hourly_data = load_hourly_trips
load_weekday_data = load_weekday_trips
load_zone_data = load_pickup_zones
load_weather_daily = load_daily_weather