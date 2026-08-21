"""BigQuery connection and query helpers for Urban Mobility Analytics."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from google.cloud import bigquery


# ============================================================
# BIGQUERY CONFIGURATION
# ============================================================

PROJECT_ID = "project-83caccc1-fe76-4d97-beb"

RAW_DATASET = "mobility_raw"
ANALYTICS_DATASET = "mobility_analytics"


# ============================================================
# BIGQUERY CLIENT
# ============================================================

@st.cache_resource
def get_client() -> bigquery.Client:
    """Create and cache the BigQuery client."""

    return bigquery.Client(
        project=PROJECT_ID
    )


# ============================================================
# GENERIC QUERY EXECUTION
# ============================================================

@st.cache_data(ttl=600)
def query_to_dataframe(
    query: str,
) -> pd.DataFrame:
    """Execute a BigQuery SQL query and return a DataFrame."""

    client = get_client()

    return client.query(
        query
    ).to_dataframe()


# ============================================================
# ANALYTICS TABLE LOADER
# ============================================================

def load_analytics_table(
    table_name: str,
) -> pd.DataFrame:
    """
    Load a verified analytical table from BigQuery.

    Only tables that actually exist in
    mobility_analytics are allowed.
    """

    allowed_tables = {
        "monthly_trip_summary_2021",
        "hourly_trip_summary_2021",
        "weekday_trip_summary_2021",
        "pickup_zone_summary_2021",
        "weather_demand_daily_2021",
        "weather_impact_summary_2021",
        "temperature_impact_2021",
        "precipitation_impact_2021",
        "snowfall_impact_2021",
        "wind_impact_2021",
        "weekday_weather_impact_2021",
        "taxi_revenue_weather_daily_2021",
        "taxi_revenue_weather_impact_2021",
    }

    if table_name not in allowed_tables:
        raise ValueError(
            f"Unknown analytics table: {table_name}"
        )

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{ANALYTICS_DATASET}.{table_name}`
    """

    return query_to_dataframe(query)


# ============================================================
# RAW WEATHER TABLE
# ============================================================

def load_raw_weather() -> pd.DataFrame:
    """
    Load the raw daily weather table.

    This table is stored in mobility_raw and is used
    by the weather ingestion / transformation pipeline.
    """

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{RAW_DATASET}.daily_weather_2021`
    """

    return query_to_dataframe(query)