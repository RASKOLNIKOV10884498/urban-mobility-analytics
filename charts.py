"""Plotly charts for Urban Mobility Analytics."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# HELPERS
# ============================================================

def _empty_figure(title: str, message: str) -> go.Figure:
    """Return a safe empty Plotly figure."""

    fig = go.Figure()

    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )

    fig.update_layout(
        title=title,
        template="plotly_white",
    )

    return fig


def _require_columns(
    data: pd.DataFrame,
    columns: list[str],
    chart_name: str,
) -> None:
    """Validate required dataframe columns."""

    missing = [
        column
        for column in columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"{chart_name} is missing columns: "
            + ", ".join(missing)
            + f". Available columns: {list(data.columns)}"
        )


# ============================================================
# MOBILITY DEMAND
# ============================================================

def monthly_trip_chart(
    monthly_trips: pd.DataFrame,
) -> go.Figure:
    """Create monthly trip demand chart."""

    if monthly_trips.empty:
        return _empty_figure(
            "Monthly Trip Demand",
            "No monthly trip data available.",
        )

    _require_columns(
        monthly_trips,
        ["month", "total_trips"],
        "monthly_trip_chart",
    )

    data = monthly_trips.copy()

    fig = px.line(
        data,
        x="month",
        y="total_trips",
        markers=True,
        title="Monthly Trip Demand",
        labels={
            "month": "Month",
            "total_trips": "Total trips",
        },
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total trips",
        template="plotly_white",
    )

    return fig


def hourly_trip_chart(
    hourly_trips: pd.DataFrame,
) -> go.Figure:
    """Create hourly trip demand chart."""

    if hourly_trips.empty:
        return _empty_figure(
            "Trip Demand by Hour",
            "No hourly trip data available.",
        )

    x_column = (
        "pickup_hour"
        if "pickup_hour" in hourly_trips.columns
        else "hour"
        if "hour" in hourly_trips.columns
        else None
    )

    if x_column is None:
        raise ValueError(
            "hourly_trip_chart requires 'pickup_hour' "
            "or 'hour'."
        )

    y_column = (
        "avg_trips"
        if "avg_trips" in hourly_trips.columns
        else "total_trips"
        if "total_trips" in hourly_trips.columns
        else None
    )

    if y_column is None:
        raise ValueError(
            "hourly_trip_chart requires 'avg_trips' "
            "or 'total_trips'."
        )

    y_label = (
        "Average trips"
        if y_column == "avg_trips"
        else "Total trips"
    )

    data = hourly_trips.copy()

    if pd.api.types.is_numeric_dtype(data[x_column]):
        data = data.sort_values(x_column)

    fig = px.line(
        data,
        x=x_column,
        y=y_column,
        markers=True,
        title="Trip Demand by Hour",
        labels={
            x_column: "Hour of day",
            y_column: y_label,
        },
    )

    fig.update_layout(
        xaxis_title="Hour of day",
        yaxis_title=y_label,
        template="plotly_white",
    )

    return fig


def weekday_trip_chart(
    weekday_trips: pd.DataFrame,
) -> go.Figure:
    """Create weekday trip demand chart."""

    if weekday_trips.empty:
        return _empty_figure(
            "Trip Demand by Weekday",
            "No weekday data available.",
        )

    _require_columns(
        weekday_trips,
        ["day_of_week", "total_trips"],
        "weekday_trip_chart",
    )

    data = weekday_trips.copy()

    if "day_number" in data.columns:
        data = data.sort_values("day_number")

    y_column = (
        "avg_daily_trips"
        if "avg_daily_trips" in data.columns
        else "total_trips"
    )

    y_label = (
        "Average daily trips"
        if y_column == "avg_daily_trips"
        else "Total trips"
    )

    fig = px.bar(
        data,
        x="day_of_week",
        y=y_column,
        title="Trip Demand by Weekday",
        labels={
            "day_of_week": "Day",
            y_column: y_label,
        },
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=y_label,
        template="plotly_white",
    )

    return fig


# ============================================================
# GEOGRAPHIC ANALYSIS
# ============================================================

def top_zone_chart(
    zones: pd.DataFrame,
) -> go.Figure:
    """Create top pickup-zone chart."""

    if zones.empty:
        return _empty_figure(
            "Top Pickup Zones",
            "No pickup-zone data available.",
        )

    _require_columns(
        zones,
        ["pickup_zone", "total_trips"],
        "top_zone_chart",
    )

    data = zones.copy()

    data = (
        data
        .sort_values("total_trips", ascending=False)
        .head(15)
        .sort_values("total_trips", ascending=True)
    )

    hover_columns = [
        column
        for column in [
            "borough",
            "avg_trip_distance_miles",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="total_trips",
        y="pickup_zone",
        orientation="h",
        title="Top 15 Pickup Zones",
        labels={
            "pickup_zone": "Pickup zone",
            "total_trips": "Total trips",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title="Total trips",
        yaxis_title=None,
        template="plotly_white",
    )

    return fig


def pickup_zone_chart(
    zones: pd.DataFrame,
) -> go.Figure:
    """Dashboard-facing pickup-zone chart."""

    return top_zone_chart(zones)


# ============================================================
# WEATHER DEMAND
# ============================================================

def weather_demand_chart(
    weather_impact: pd.DataFrame,
) -> go.Figure:
    """Create demand comparison by weather condition."""

    if weather_impact.empty:
        return _empty_figure(
            "Average Daily Trips by Weather",
            "No weather data available.",
        )

    _require_columns(
        weather_impact,
        ["weather_condition", "avg_daily_trips"],
        "weather_demand_chart",
    )

    data = weather_impact.sort_values(
        "avg_daily_trips",
        ascending=True,
    )

    hover_columns = [
        column
        for column in [
            "days_in_category",
            "avg_trip_distance_miles",
            "avg_temperature_f",
            "avg_precipitation_inches",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="avg_daily_trips",
        y="weather_condition",
        orientation="h",
        title="Average Daily Trips by Weather",
        labels={
            "weather_condition": "Weather",
            "avg_daily_trips": "Average daily trips",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title="Average daily trips",
        yaxis_title=None,
        template="plotly_white",
    )

    return fig


# ============================================================
# TEMPERATURE
# ============================================================

def temperature_impact_chart(
    temperature_impact: pd.DataFrame,
) -> go.Figure:
    """Create demand by temperature band."""

    if temperature_impact.empty:
        return _empty_figure(
            "Demand by Temperature Band",
            "No temperature data available.",
        )

    _require_columns(
        temperature_impact,
        [
            "temperature_band",
            "band_order",
            "avg_daily_trips",
        ],
        "temperature_impact_chart",
    )

    data = temperature_impact.sort_values(
        "band_order"
    )

    hover_columns = [
        column
        for column in [
            "days_in_band",
            "avg_daily_gross_charges_usd",
            "avg_daily_tips_usd",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="temperature_band",
        y="avg_daily_trips",
        title="Demand by Temperature Band",
        labels={
            "temperature_band": "Temperature",
            "avg_daily_trips": "Average daily trips",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily trips",
        template="plotly_white",
    )

    return fig


# ============================================================
# TEMPERATURE VS DEMAND
# ============================================================

def temperature_demand_chart(
    weather_daily: pd.DataFrame,
) -> go.Figure:
    """Create daily temperature versus trip-demand scatter."""

    if weather_daily.empty:
        return _empty_figure(
            "Temperature vs Daily Trip Demand",
            "No daily weather data available.",
        )

    _require_columns(
        weather_daily,
        [
            "avg_temperature_f",
            "total_trips",
        ],
        "temperature_demand_chart",
    )

    data = weather_daily.copy()

    color_column = (
        "weather_condition"
        if "weather_condition" in data.columns
        else None
    )

    hover_columns = [
        column
        for column in [
            "trip_date",
            "avg_trip_distance_miles",
            "max_temperature_f",
            "precipitation_inches",
            "snowfall_inches",
            "max_wind_speed_mph",
            "weather_code",
        ]
        if column in data.columns
    ]

    fig = px.scatter(
        data,
        x="avg_temperature_f",
        y="total_trips",
        color=color_column,
        hover_data=hover_columns,
        title="Temperature vs Daily Trip Demand",
        labels={
            "avg_temperature_f": "Average temperature (°F)",
            "total_trips": "Daily trips",
            "weather_condition": "Weather",
        },
    )

    fig.update_layout(
        xaxis_title="Average temperature (°F)",
        yaxis_title="Daily trips",
        template="plotly_white",
    )

    return fig


# ============================================================
# PRECIPITATION
# ============================================================

def precipitation_demand_chart(
    precipitation_impact: pd.DataFrame,
) -> go.Figure:
    """Create demand by precipitation band."""

    if precipitation_impact.empty:
        return _empty_figure(
            "Demand by Precipitation Conditions",
            "No precipitation data available.",
        )

    _require_columns(
        precipitation_impact,
        [
            "precipitation_band",
            "band_order",
            "avg_daily_trips",
        ],
        "precipitation_demand_chart",
    )

    data = precipitation_impact.sort_values(
        "band_order"
    )

    hover_columns = [
        column
        for column in [
            "days_in_band",
            "avg_daily_gross_charges_usd",
            "avg_daily_tips_usd",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="precipitation_band",
        y="avg_daily_trips",
        title="Demand by Precipitation Conditions",
        labels={
            "precipitation_band": "Precipitation",
            "avg_daily_trips": "Average daily trips",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily trips",
        template="plotly_white",
    )

    return fig


def precipitation_impact_chart(
    precipitation_impact: pd.DataFrame,
) -> go.Figure:
    """Dashboard-facing precipitation chart."""

    return precipitation_demand_chart(
        precipitation_impact
    )


# ============================================================
# SNOWFALL
# ============================================================

def snowfall_demand_chart(
    snowfall_impact: pd.DataFrame,
) -> go.Figure:
    """Create demand by snowfall band."""

    if snowfall_impact.empty:
        return _empty_figure(
            "Demand by Snowfall Conditions",
            "No snowfall data available.",
        )

    _require_columns(
        snowfall_impact,
        [
            "snowfall_band",
            "band_order",
            "avg_daily_trips",
        ],
        "snowfall_demand_chart",
    )

    data = snowfall_impact.sort_values(
        "band_order"
    )

    hover_columns = [
        column
        for column in [
            "days_in_band",
            "avg_daily_gross_charges_usd",
            "avg_daily_tips_usd",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="snowfall_band",
        y="avg_daily_trips",
        title="Demand by Snowfall Conditions",
        labels={
            "snowfall_band": "Snowfall",
            "avg_daily_trips": "Average daily trips",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily trips",
        template="plotly_white",
    )

    return fig


def snowfall_impact_chart(
    snowfall_impact: pd.DataFrame,
) -> go.Figure:
    """Dashboard-facing snowfall chart."""

    return snowfall_demand_chart(
        snowfall_impact
    )


# ============================================================
# WIND
# ============================================================

def wind_demand_chart(
    wind_impact: pd.DataFrame,
) -> go.Figure:
    """Create demand by wind band."""

    if wind_impact.empty:
        return _empty_figure(
            "Demand by Wind Conditions",
            "No wind data available.",
        )

    _require_columns(
        wind_impact,
        [
            "wind_band",
            "band_order",
            "avg_daily_trips",
        ],
        "wind_demand_chart",
    )

    data = wind_impact.sort_values(
        "band_order"
    )

    hover_columns = [
        column
        for column in [
            "days_in_band",
            "avg_daily_gross_charges_usd",
            "avg_daily_tips_usd",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="wind_band",
        y="avg_daily_trips",
        title="Demand by Wind Conditions",
        labels={
            "wind_band": "Wind",
            "avg_daily_trips": "Average daily trips",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily trips",
        template="plotly_white",
    )

    return fig


def wind_impact_chart(
    wind_impact: pd.DataFrame,
) -> go.Figure:
    """Dashboard-facing wind chart."""

    return wind_demand_chart(wind_impact)


# ============================================================
# WEATHER × WEEKDAY
# ============================================================

def weekday_weather_chart(
    weekday_weather: pd.DataFrame,
) -> go.Figure:
    """Create weather demand comparison across weekdays."""

    if weekday_weather.empty:
        return _empty_figure(
            "Weather × Weekday Demand",
            "No weekday-weather data available.",
        )

    _require_columns(
        weekday_weather,
        [
            "day_of_week",
            "weather_condition",
            "avg_daily_trips",
        ],
        "weekday_weather_chart",
    )

    data = weekday_weather.copy()

    if "day_number" in data.columns:
        data = data.sort_values(
            [
                "day_number",
                "weather_condition",
            ]
        )

    hover_columns = [
        column
        for column in [
            "days_in_category",
            "avg_daily_gross_charges_usd",
            "avg_daily_tips_usd",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="day_of_week",
        y="avg_daily_trips",
        color="weather_condition",
        barmode="group",
        title="Weather × Weekday Demand",
        labels={
            "day_of_week": "Day",
            "avg_daily_trips": "Average daily trips",
            "weather_condition": "Weather",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily trips",
        template="plotly_white",
    )

    return fig


# ============================================================
# REVENUE
# ============================================================

def revenue_weather_chart(
    revenue_impact: pd.DataFrame,
) -> go.Figure:
    """Create revenue comparison by weather condition."""

    if revenue_impact.empty:
        return _empty_figure(
            "Average Daily Gross Charges by Weather",
            "No revenue data available.",
        )

    _require_columns(
        revenue_impact,
        [
            "weather_condition",
            "avg_daily_gross_customer_charges_usd",
        ],
        "revenue_weather_chart",
    )

    data = revenue_impact.sort_values(
        "avg_daily_gross_customer_charges_usd",
        ascending=True,
    )

    hover_columns = [
        column
        for column in [
            "days_in_category",
            "total_gross_customer_charges_usd",
            "avg_daily_tips_usd",
            "avg_customer_charge_per_trip_usd",
            "avg_daily_trips",
        ]
        if column in data.columns
    ]

    fig = px.bar(
        data,
        x="avg_daily_gross_customer_charges_usd",
        y="weather_condition",
        orientation="h",
        title="Average Daily Gross Charges by Weather",
        labels={
            "weather_condition": "Weather",
            "avg_daily_gross_customer_charges_usd":
                "Average daily gross charges (USD)",
        },
        hover_data=hover_columns,
    )

    fig.update_layout(
        xaxis_title="Average daily gross charges (USD)",
        yaxis_title=None,
        template="plotly_white",
    )

    return fig


def weather_revenue_chart(
    revenue_impact: pd.DataFrame,
) -> go.Figure:
    """Dashboard-facing weather-revenue chart."""

    return revenue_weather_chart(
        revenue_impact
    )


# ============================================================
# REVENUE BY TEMPERATURE
# ============================================================

def temperature_revenue_chart(
    temperature_impact: pd.DataFrame,
) -> go.Figure:
    """Create average daily revenue by temperature band."""

    if temperature_impact.empty:
        return _empty_figure(
            "Revenue by Temperature Band",
            "No temperature revenue data available.",
        )

    _require_columns(
        temperature_impact,
        [
            "temperature_band",
            "band_order",
            "avg_daily_gross_charges_usd",
        ],
        "temperature_revenue_chart",
    )

    data = temperature_impact.sort_values(
        "band_order"
    )

    fig = px.bar(
        data,
        x="temperature_band",
        y="avg_daily_gross_charges_usd",
        title="Average Daily Revenue by Temperature",
        labels={
            "temperature_band": "Temperature",
            "avg_daily_gross_charges_usd":
                "Average daily gross charges (USD)",
        },
        hover_data=[
            column
            for column in [
                "days_in_band",
                "avg_daily_trips",
                "avg_daily_tips_usd",
            ]
            if column in data.columns
        ],
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily gross charges (USD)",
        template="plotly_white",
    )

    return fig


# ============================================================
# PRECIPITATION REVENUE
# ============================================================

def precipitation_revenue_chart(
    precipitation_impact: pd.DataFrame,
) -> go.Figure:
    """Create average daily revenue by precipitation band."""

    if precipitation_impact.empty:
        return _empty_figure(
            "Revenue by Precipitation",
            "No precipitation revenue data available.",
        )

    _require_columns(
        precipitation_impact,
        [
            "precipitation_band",
            "band_order",
            "avg_daily_gross_charges_usd",
        ],
        "precipitation_revenue_chart",
    )

    data = precipitation_impact.sort_values(
        "band_order"
    )

    fig = px.bar(
        data,
        x="precipitation_band",
        y="avg_daily_gross_charges_usd",
        title="Average Daily Revenue by Precipitation",
        labels={
            "precipitation_band": "Precipitation",
            "avg_daily_gross_charges_usd":
                "Average daily gross charges (USD)",
        },
        hover_data=[
            column
            for column in [
                "days_in_band",
                "avg_daily_trips",
                "avg_daily_tips_usd",
            ]
            if column in data.columns
        ],
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily gross charges (USD)",
        template="plotly_white",
    )

    return fig


# ============================================================
# SNOWFALL REVENUE
# ============================================================

def snowfall_revenue_chart(
    snowfall_impact: pd.DataFrame,
) -> go.Figure:
    """Create average daily revenue by snowfall band."""

    if snowfall_impact.empty:
        return _empty_figure(
            "Revenue by Snowfall",
            "No snowfall revenue data available.",
        )

    _require_columns(
        snowfall_impact,
        [
            "snowfall_band",
            "band_order",
            "avg_daily_gross_charges_usd",
        ],
        "snowfall_revenue_chart",
    )

    data = snowfall_impact.sort_values(
        "band_order"
    )

    fig = px.bar(
        data,
        x="snowfall_band",
        y="avg_daily_gross_charges_usd",
        title="Average Daily Revenue by Snowfall",
        labels={
            "snowfall_band": "Snowfall",
            "avg_daily_gross_charges_usd":
                "Average daily gross charges (USD)",
        },
        hover_data=[
            column
            for column in [
                "days_in_band",
                "avg_daily_trips",
                "avg_daily_tips_usd",
            ]
            if column in data.columns
        ],
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily gross charges (USD)",
        template="plotly_white",
    )

    return fig


# ============================================================
# WIND REVENUE
# ============================================================

def wind_revenue_chart(
    wind_impact: pd.DataFrame,
) -> go.Figure:
    """Create average daily revenue by wind band."""

    if wind_impact.empty:
        return _empty_figure(
            "Revenue by Wind Conditions",
            "No wind revenue data available.",
        )

    _require_columns(
        wind_impact,
        [
            "wind_band",
            "band_order",
            "avg_daily_gross_charges_usd",
        ],
        "wind_revenue_chart",
    )

    data = wind_impact.sort_values(
        "band_order"
    )

    fig = px.bar(
        data,
        x="wind_band",
        y="avg_daily_gross_charges_usd",
        title="Average Daily Revenue by Wind",
        labels={
            "wind_band": "Wind",
            "avg_daily_gross_charges_usd":
                "Average daily gross charges (USD)",
        },
        hover_data=[
            column
            for column in [
                "days_in_band",
                "avg_daily_trips",
                "avg_daily_tips_usd",
            ]
            if column in data.columns
        ],
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="Average daily gross charges (USD)",
        template="plotly_white",
    )

    return fig