# Urban Mobility Analytics

A Streamlit dashboard using BigQuery summaries of NYC Green Taxi trips from 2021.

## What is already in BigQuery

The dashboard expects these tables in `project-83caccc1-fe76-4d97-beb.mobility_analytics`:

- `monthly_trip_summary_2021`
- `hourly_trip_summary_2021`
- `weekday_trip_summary_2021`
- `pickup_zone_summary_2021`

## First-time local setup

1. Open a terminal in this folder.
2. Create and activate a Python virtual environment.
3. Install the dependencies: `python3 -m pip install -r requirements.txt`.
4. Sign in securely to Google Cloud: `gcloud auth application-default login`.
5. Start the dashboard: `streamlit run app.py`.

The Google sign-in opens a browser window. It stores your local development credentials on your computer, not in this project. Never commit a downloaded service-account key to source control.

## Load weather data

After the local setup, run `python ingest_weather.py`. The script fetches one daily NYC weather record for each day of 2021 from Open-Meteo and replaces `mobility_raw.daily_weather_2021` in BigQuery.
