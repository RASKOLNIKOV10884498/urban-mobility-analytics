"""Fetch daily NYC weather from Open-Meteo and load it into BigQuery."""

from __future__ import annotations

import pandas as pd
import requests
from google.cloud import bigquery


# ============================================================
# BIGQUERY CONFIGURATION
# ============================================================

PROJECT_ID = "project-83caccc1-fe76-4d97-beb"
RAW_DATASET = "mobility_raw"
WEATHER_TABLE = "daily_weather_2021"

TABLE_ID = f"{PROJECT_ID}.{RAW_DATASET}.{WEATHER_TABLE}"

# ============================================================
# OPEN-METEO CONFIGURATION
# ============================================================

API_URL = "https://archive-api.open-meteo.com/v1/archive"

NEW_YORK_LATITUDE = 40.7128
NEW_YORK_LONGITUDE = -74.0060

START_DATE = "2021-01-01"
END_DATE = "2021-12-31"


# ============================================================
# FETCH WEATHER
# ============================================================

def fetch_weather() -> pd.DataFrame:
    """
    Fetch one daily weather record for each day of 2021
    for New York City.
    """

    parameters = {
        "latitude": NEW_YORK_LATITUDE,
        "longitude": NEW_YORK_LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": (
            "temperature_2m_mean,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "rain_sum,"
            "snowfall_sum,"
            "weather_code,"
            "wind_speed_10m_max"
        ),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/New_York",
    }

    response = requests.get(
        API_URL,
        params=parameters,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    if "daily" not in payload:
        raise ValueError(
            "Open-Meteo response does not contain daily weather data."
        )

    weather = pd.DataFrame(payload["daily"])

    if weather.empty:
        raise ValueError(
            "Open-Meteo returned an empty weather dataset."
        )

    # --------------------------------------------------------
    # Rename API date column
    # --------------------------------------------------------

    weather = weather.rename(
        columns={
            "time": "weather_date"
        }
    )

    # --------------------------------------------------------
    # Convert date to Python date objects
    # --------------------------------------------------------

    weather["weather_date"] = pd.to_datetime(
        weather["weather_date"]
    ).dt.date

    # --------------------------------------------------------
    # Validate expected columns
    # --------------------------------------------------------

    expected_columns = [
        "weather_date",
        "temperature_2m_mean",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "weather_code",
        "wind_speed_10m_max",
    ]

    missing_columns = [
        column
        for column in expected_columns
        if column not in weather.columns
    ]

    if missing_columns:
        raise ValueError(
            "Weather API response is missing columns: "
            + ", ".join(missing_columns)
        )

    # --------------------------------------------------------
    # Keep only the columns used by the project
    # --------------------------------------------------------

    weather = weather[
        expected_columns
    ].copy()

    return weather


# ============================================================
# BIGQUERY LOAD
# ============================================================

def load_weather(weather: pd.DataFrame) -> None:
    """
    Replace the raw BigQuery weather table with the
    reproducible 2021 Open-Meteo extract.
    """

    if weather is None or weather.empty:
        raise ValueError(
            "Cannot load an empty weather DataFrame."
        )

    client = bigquery.Client(
        project=PROJECT_ID
    )

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField(
                "weather_date",
                "DATE",
            ),
            bigquery.SchemaField(
                "temperature_2m_mean",
                "FLOAT",
            ),
            bigquery.SchemaField(
                "temperature_2m_max",
                "FLOAT",
            ),
            bigquery.SchemaField(
                "temperature_2m_min",
                "FLOAT",
            ),
            bigquery.SchemaField(
                "precipitation_sum",
                "FLOAT",
            ),
            bigquery.SchemaField(
                "rain_sum",
                "FLOAT",
            ),
            bigquery.SchemaField(
                "snowfall_sum",
                "FLOAT",
            ),
            bigquery.SchemaField(
                "weather_code",
                "INTEGER",
            ),
            bigquery.SchemaField(
                "wind_speed_10m_max",
                "FLOAT",
            ),
        ],
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_dataframe(
        weather,
        TABLE_ID,
        job_config=job_config,
    )

    job.result()


# ============================================================
# VALIDATION
# ============================================================

def validate_weather(weather: pd.DataFrame) -> None:
    """Validate the downloaded 2021 weather dataset."""

    if len(weather) != 365:
        raise ValueError(
            f"Expected 365 weather rows, received {len(weather)}."
        )

    if weather["weather_date"].duplicated().any():
        raise ValueError(
            "Weather dataset contains duplicate dates."
        )

    minimum_date = weather["weather_date"].min()
    maximum_date = weather["weather_date"].max()

    if str(minimum_date) != START_DATE:
        raise ValueError(
            f"Expected first date {START_DATE}, "
            f"received {minimum_date}."
        )

    if str(maximum_date) != END_DATE:
        raise ValueError(
            f"Expected last date {END_DATE}, "
            f"received {maximum_date}."
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main() -> None:
    """Fetch, validate, and load the 2021 weather dataset."""

    print("Fetching 2021 NYC weather from Open-Meteo...")

    weather_data = fetch_weather()

    print(
        f"Fetched {len(weather_data)} weather records."
    )

    validate_weather(weather_data)

    print(
        "Weather validation passed: "
        "365 unique daily records."
    )

    print(
        f"Loading weather into BigQuery: {TABLE_ID}"
    )

    load_weather(weather_data)

    print(
        f"Successfully loaded "
        f"{len(weather_data)} daily weather records "
        f"into {TABLE_ID}."
    )


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()