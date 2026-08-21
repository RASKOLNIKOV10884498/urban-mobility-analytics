"""Analytical KPI and insight calculations for Urban Mobility Analytics."""

from __future__ import annotations

import pandas as pd


# ============================================================
# MOBILITY KPIs
# ============================================================

def get_peak_month(monthly: pd.DataFrame) -> pd.Series:
    """Return the month with the highest trip volume."""

    if monthly is None or monthly.empty:
        return pd.Series(dtype="object")

    if "total_trips" not in monthly.columns:
        return pd.Series(dtype="object")

    return monthly.loc[monthly["total_trips"].idxmax()]


def get_peak_hour(hourly: pd.DataFrame) -> pd.Series:
    """Return the hour with the highest trip volume."""

    if hourly is None or hourly.empty:
        return pd.Series(dtype="object")

    if "total_trips" not in hourly.columns:
        return pd.Series(dtype="object")

    return hourly.loc[hourly["total_trips"].idxmax()]


def get_peak_weekday(weekday: pd.DataFrame) -> pd.Series:
    """Return the weekday with the highest trip volume."""

    if weekday is None or weekday.empty:
        return pd.Series(dtype="object")

    if "avg_daily_trips" in weekday.columns:
        metric = "avg_daily_trips"
    elif "total_trips" in weekday.columns:
        metric = "total_trips"
    else:
        return pd.Series(dtype="object")

    return weekday.loc[weekday[metric].idxmax()]


def get_top_pickup_zone(zones: pd.DataFrame) -> pd.Series:
    """Return the pickup zone with the highest trip volume."""

    if zones is None or zones.empty:
        return pd.Series(dtype="object")

    if "total_trips" not in zones.columns:
        return pd.Series(dtype="object")

    return zones.loc[zones["total_trips"].idxmax()]


def get_total_trips(monthly: pd.DataFrame) -> int:
    """Return total trips represented by the monthly summary."""

    if monthly is None or monthly.empty:
        return 0

    if "total_trips" not in monthly.columns:
        return 0

    return int(monthly["total_trips"].sum())


def get_average_trip_distance(
    monthly: pd.DataFrame,
) -> float:
    """Return the mean monthly average trip distance."""

    if monthly is None or monthly.empty:
        return 0.0

    if "avg_trip_distance_miles" not in monthly.columns:
        return 0.0

    return float(
        monthly["avg_trip_distance_miles"].mean()
    )


# ============================================================
# DASHBOARD OVERVIEW METRICS
# ============================================================

def calculate_overview_metrics(
    daily_weather: pd.DataFrame,
    revenue_impact: pd.DataFrame | None = None,
) -> dict[str, float]:
    """
    Calculate dashboard overview KPIs.

    Mobility metrics come from weather_demand_daily_2021.

    Revenue metrics come from
    taxi_revenue_weather_impact_2021 because the daily
    weather-demand table does not contain revenue fields.
    """

    result = {
        "total_trips": 0.0,
        "avg_daily_trips": 0.0,
        "avg_daily_gross_charges_usd": 0.0,
        "avg_daily_tips_usd": 0.0,
    }

    # --------------------------------------------------------
    # MOBILITY
    # --------------------------------------------------------

    if daily_weather is not None and not daily_weather.empty:

        if "total_trips" in daily_weather.columns:

            result["total_trips"] = float(
                daily_weather["total_trips"].sum()
            )

            result["avg_daily_trips"] = float(
                daily_weather["total_trips"].mean()
            )

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    if revenue_impact is not None and not revenue_impact.empty:

        if "avg_daily_gross_customer_charges_usd" in revenue_impact.columns:

            result["avg_daily_gross_charges_usd"] = float(
                revenue_impact[
                    "avg_daily_gross_customer_charges_usd"
                ].mean()
            )

        if "avg_daily_tips_usd" in revenue_impact.columns:

            result["avg_daily_tips_usd"] = float(
                revenue_impact[
                    "avg_daily_tips_usd"
                ].mean()
            )

    return result


# ============================================================
# WEATHER ANALYSIS
# ============================================================

def get_weather_comparison(
    weather_impact: pd.DataFrame,
) -> pd.DataFrame:
    """Compare each weather category with dry-day demand."""

    if weather_impact is None:
        return pd.DataFrame()

    result = weather_impact.copy()

    if result.empty:
        result["vs_dry_pct"] = pd.Series(
            dtype="float64"
        )
        return result

    required_columns = {
        "weather_condition",
        "avg_daily_trips",
    }

    if not required_columns.issubset(result.columns):
        result["vs_dry_pct"] = float("nan")
        return result

    dry_rows = result.loc[
        result["weather_condition"].eq("Dry"),
        "avg_daily_trips",
    ]

    if dry_rows.empty:
        result["vs_dry_pct"] = float("nan")
        return result

    dry_demand = float(dry_rows.iloc[0])

    if dry_demand == 0:
        result["vs_dry_pct"] = float("nan")
        return result

    result["vs_dry_pct"] = (
        (
            result["avg_daily_trips"]
            - dry_demand
        )
        / dry_demand
        * 100
    )

    return result


def get_weather_extremes(
    weather_impact: pd.DataFrame,
) -> tuple[pd.Series, pd.Series]:
    """Return weather categories with highest and lowest demand."""

    if weather_impact is None or weather_impact.empty:
        empty = pd.Series(dtype="object")
        return empty, empty

    if "avg_daily_trips" not in weather_impact.columns:
        empty = pd.Series(dtype="object")
        return empty, empty

    highest = weather_impact.loc[
        weather_impact["avg_daily_trips"].idxmax()
    ]

    lowest = weather_impact.loc[
        weather_impact["avg_daily_trips"].idxmin()
    ]

    return highest, lowest


# ============================================================
# REVENUE ANALYSIS
# ============================================================

def get_revenue_totals(
    revenue_data: pd.DataFrame,
) -> dict[str, float]:
    """
    Calculate revenue metrics.

    Compatible with both:

        taxi_revenue_weather_impact_2021

    and

        taxi_revenue_weather_daily_2021
    """

    result = {
        "gross_charges": 0.0,
        "tips": 0.0,
        "average_daily_charges": 0.0,
        "average_charge_per_trip": 0.0,
    }

    if revenue_data is None or revenue_data.empty:
        return result

    # --------------------------------------------------------
    # Gross charges
    # --------------------------------------------------------

    if "total_gross_customer_charges_usd" in revenue_data.columns:

        result["gross_charges"] = float(
            revenue_data[
                "total_gross_customer_charges_usd"
            ].sum()
        )

    elif "gross_customer_charges_usd" in revenue_data.columns:

        result["gross_charges"] = float(
            revenue_data[
                "gross_customer_charges_usd"
            ].sum()
        )

    # --------------------------------------------------------
    # Average daily gross charges
    # --------------------------------------------------------

    if "avg_daily_gross_customer_charges_usd" in revenue_data.columns:

        result["average_daily_charges"] = float(
            revenue_data[
                "avg_daily_gross_customer_charges_usd"
            ].mean()
        )

    elif "gross_customer_charges_usd" in revenue_data.columns:

        result["average_daily_charges"] = float(
            revenue_data[
                "gross_customer_charges_usd"
            ].mean()
        )

    # --------------------------------------------------------
    # Tips
    # --------------------------------------------------------

    if "avg_daily_tips_usd" in revenue_data.columns:

        result["tips"] = float(
            revenue_data[
                "avg_daily_tips_usd"
            ].mean()
        )

    elif "total_tips_usd" in revenue_data.columns:

        result["tips"] = float(
            revenue_data[
                "total_tips_usd"
            ].sum()
        )

    # --------------------------------------------------------
    # Average charge per trip
    # --------------------------------------------------------

    if "avg_customer_charge_per_trip_usd" in revenue_data.columns:

        result["average_charge_per_trip"] = float(
            revenue_data[
                "avg_customer_charge_per_trip_usd"
            ].mean()
        )

    elif "avg_customer_charge_usd" in revenue_data.columns:

        result["average_charge_per_trip"] = float(
            revenue_data[
                "avg_customer_charge_usd"
            ].mean()
        )

    return result


def get_revenue_metrics(
    revenue_data: pd.DataFrame,
) -> dict[str, float]:
    """Return dashboard-ready revenue KPIs."""

    return get_revenue_totals(revenue_data)