"""Executive dashboard for Urban Mobility Analytics."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import (
    load_daily_weather,
    load_hourly_trips,
    load_monthly_trips,
    load_revenue_weather_impact,
    load_weekday_trips,
)

from charts import (
    hourly_trip_chart,
    monthly_trip_chart,
    weekday_trip_chart,
    revenue_weather_chart,
)

from metrics import (
    calculate_overview_metrics,
    get_peak_hour,
    get_peak_month,
    get_peak_weekday,
)


st.set_page_config(
    page_title="Executive Dashboard | Urban Mobility Analytics",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .executive-hero {
        padding: 2rem 2.2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(128,128,128,0.20);
        background: linear-gradient(
            135deg,
            rgba(30, 41, 59, 0.95),
            rgba(15, 23, 42, 0.95)
        );
    }

    .executive-hero h1 {
        margin: 0;
        font-size: 2.4rem;
        line-height: 1.1;
    }

    .executive-hero p {
        margin-top: 0.8rem;
        margin-bottom: 0;
        font-size: 1.05rem;
        opacity: 0.88;
    }

    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.65;
        margin-bottom: 0.25rem;
    }

    .section-title {
        font-size: 1.55rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .section-description {
        opacity: 0.72;
        margin-bottom: 1rem;
    }

    .insight-card {
        border: 1px solid rgba(128,128,128,0.20);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        height: 100%;
        background: rgba(128,128,128,0.035);
    }

    .insight-card h4 {
        margin-top: 0;
        margin-bottom: 0.55rem;
    }

    .insight-card p {
        margin-bottom: 0.35rem;
        line-height: 1.55;
    }

    .executive-callout {
        border-left: 4px solid currentColor;
        padding: 1rem 1.2rem;
        margin: 0.75rem 0 1.25rem 0;
        border-radius: 0 10px 10px 0;
        background: rgba(128,128,128,0.045);
    }

    .small-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.65;
        font-weight: 700;
    }

    .big-number {
        font-size: 2rem;
        font-weight: 750;
        margin-top: 0.15rem;
    }

    .metric-context {
        font-size: 0.85rem;
        opacity: 0.65;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.18);
        padding: 1rem;
        border-radius: 14px;
        background: rgba(128,128,128,0.035);
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    .status-good {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background: rgba(34,197,94,0.10);
        border: 1px solid rgba(34,197,94,0.20);
    }

    .status-watch {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background: rgba(245,158,11,0.10);
        border: 1px solid rgba(245,158,11,0.20);
    }

    .status-risk {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background: rgba(239,68,68,0.10);
        border: 1px solid rgba(239,68,68,0.20);
    }

    .footer-note {
        text-align: center;
        opacity: 0.55;
        font-size: 0.82rem;
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


monthly_trips = load_monthly_trips()
hourly_trips = load_hourly_trips()
weekday_trips = load_weekday_trips()
daily_weather = load_daily_weather()
revenue_impact = load_revenue_weather_impact()


def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def format_money(value):
    return f"${safe_float(value):,.0f}"


def format_number(value):
    return f"{safe_float(value):,.0f}"


def format_percent(value):
    return f"{safe_float(value):.1f}%"


def get_row(dataframe, column, value):
    if dataframe is None or dataframe.empty:
        return pd.Series(dtype="object")

    if column not in dataframe.columns:
        return pd.Series(dtype="object")

    rows = dataframe[dataframe[column].eq(value)]

    if rows.empty:
        return pd.Series(dtype="object")

    return rows.iloc[0]


def calculate_daily_demand():
    if (
        daily_weather is not None
        and not daily_weather.empty
        and "total_trips" in daily_weather.columns
    ):
        return safe_float(
            daily_weather["total_trips"].mean()
        )

    if (
        monthly_trips is not None
        and not monthly_trips.empty
        and "total_trips" in monthly_trips.columns
    ):
        total = safe_float(
            monthly_trips["total_trips"].sum()
        )

        return total / 365 if total else 0.0

    return 0.0


def calculate_total_trips():
    if (
        monthly_trips is not None
        and not monthly_trips.empty
        and "total_trips" in monthly_trips.columns
    ):
        return safe_float(
            monthly_trips["total_trips"].sum()
        )

    if (
        daily_weather is not None
        and not daily_weather.empty
        and "total_trips" in daily_weather.columns
    ):
        return safe_float(
            daily_weather["total_trips"].sum()
        )

    return 0.0


def get_weather_revenue(condition):
    return get_row(
        revenue_impact,
        "weather_condition",
        condition,
    )


def get_weather_demand(condition):
    return get_row(
        revenue_impact,
        "weather_condition",
        condition,
    )


def calculate_weather_difference(
    condition,
    column,
):
    dry = get_weather_revenue("Dry")
    target = get_weather_revenue(condition)

    if dry.empty or target.empty:
        return None

    if column not in dry.index or column not in target.index:
        return None

    dry_value = safe_float(dry[column])
    target_value = safe_float(target[column])

    return target_value - dry_value


def calculate_weather_percentage(
    condition,
    column,
):
    dry = get_weather_revenue("Dry")
    target = get_weather_revenue(condition)

    if dry.empty or target.empty:
        return None

    if column not in dry.index or column not in target.index:
        return None

    dry_value = safe_float(dry[column])
    target_value = safe_float(target[column])

    if dry_value == 0:
        return None

    return (
        (target_value - dry_value)
        / dry_value
        * 100
    )


total_trips = calculate_total_trips()
avg_daily_trips = calculate_daily_demand()

overview = calculate_overview_metrics(
    daily_weather=None,
    revenue_impact=revenue_impact,
)


avg_daily_revenue = safe_float(
    overview.get(
        "avg_daily_gross_charges_usd",
        0,
    )
)

avg_daily_tips = safe_float(
    overview.get(
        "avg_daily_tips_usd",
        0,
    )
)


st.markdown(
    """
    <div class="executive-hero">
        <div class="section-label">
            URBAN MOBILITY ANALYTICS
        </div>
        <h1>Executive Mobility Dashboard</h1>
        <p>
            A decision-support view of 2021 taxi demand,
            operating concentration, financial performance,
            and weather exposure across the NYC mobility system.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="section-label">EXECUTIVE PULSE</div>
    <div class="section-title">What happened across the mobility system?</div>
    <div class="section-description">
        The headline indicators establish the scale of demand,
        the normal operating baseline, and the financial activity
        represented by the historical taxi dataset.
    </div>
    """,
    unsafe_allow_html=True,
)


kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:
    st.metric(
        "Annual Taxi Trips",
        format_number(total_trips),
        help="Total taxi trips represented in the 2021 analytical dataset.",
    )


with kpi2:
    st.metric(
        "Average Daily Demand",
        format_number(avg_daily_trips),
        help="Average number of taxi trips observed per day.",
    )


with kpi3:
    st.metric(
        "Avg Daily Gross Charges",
        format_money(avg_daily_revenue),
        help="Average daily gross customer charges represented in the revenue analysis.",
    )


with kpi4:
    st.metric(
        "Avg Daily Tips",
        format_money(avg_daily_tips),
        help="Average daily customer tips represented in the analytical dataset.",
    )


st.markdown(
    """
    <div class="executive-callout">
        <strong>Executive interpretation:</strong>
        The dashboard establishes a baseline of approximately
        one million annual taxi trips and several thousand trips
        per day. Every downstream weather, time, revenue, and
        spatial analysis should be interpreted relative to this
        baseline rather than as an isolated percentage or chart.
    </div>
    """,
    unsafe_allow_html=True,
)


st.divider()


st.markdown(
    """
    <div class="section-label">OPERATING RHYTHM</div>
    <div class="section-title">When is the network under the most pressure?</div>
    <div class="section-description">
        Peak periods identify when demand is concentrated rather
        than evenly distributed across the year, day, and week.
    </div>
    """,
    unsafe_allow_html=True,
)


peak_month = get_peak_month(monthly_trips)
peak_hour = get_peak_hour(hourly_trips)
peak_weekday = get_peak_weekday(weekday_trips)


peak1, peak2, peak3 = st.columns(3)


with peak1:
    if not peak_month.empty:
        month_value = peak_month.get(
            "month",
            "N/A",
        )

        month_trips = safe_float(
            peak_month.get(
                "total_trips",
                0,
            )
        )

        st.metric(
            "Peak Month",
            str(month_value),
            f"{month_trips:,.0f} trips",
        )
    else:
        st.metric(
            "Peak Month",
            "N/A",
        )


with peak2:
    if not peak_hour.empty:
        hour_column = (
            "pickup_hour"
            if "pickup_hour" in peak_hour.index
            else "hour"
        )

        trip_column = (
            "avg_trips"
            if "avg_trips" in peak_hour.index
            else "total_trips"
        )

        hour_value = peak_hour.get(
            hour_column,
            "N/A",
        )

        hour_trips = safe_float(
            peak_hour.get(
                trip_column,
                0,
            )
        )

        st.metric(
            "Peak Hour",
            str(hour_value),
            f"{hour_trips:,.0f} trips",
        )
    else:
        st.metric(
            "Peak Hour",
            "N/A",
        )


with peak3:
    if not peak_weekday.empty:
        weekday_value = peak_weekday.get(
            "day_of_week",
            "N/A",
        )

        weekday_column = (
            "avg_daily_trips"
            if "avg_daily_trips" in peak_weekday.index
            else "total_trips"
        )

        weekday_trips_value = safe_float(
            peak_weekday.get(
                weekday_column,
                0,
            )
        )

        st.metric(
            "Peak Weekday",
            str(weekday_value),
            f"{weekday_trips_value:,.0f} trips",
        )
    else:
        st.metric(
            "Peak Weekday",
            "N/A",
        )


if not peak_month.empty:
    st.markdown(
        f"""
        <div class="insight-card">
            <h4>📌 Operating interpretation</h4>
            <p>
                Demand is not evenly distributed throughout the
                year. <strong>{peak_month.get("month", "N/A")}</strong>
                is the highest-volume month in the historical dataset,
                with approximately
                <strong>{safe_float(peak_month.get("total_trips", 0)):,.0f}</strong>
                trips.
            </p>
            <p>
                This concentration is important for workforce planning,
                fleet availability, maintenance scheduling, and
                understanding whether individual months represent
                unusually strong or weak operating environments.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.divider()


st.markdown(
    """
    <div class="section-label">DEMAND PROFILE</div>
    <div class="section-title">How does demand move through time?</div>
    <div class="section-description">
        The temporal profile separates seasonal demand from
        intraday and weekly operating behavior.
    </div>
    """,
    unsafe_allow_html=True,
)


monthly_col1, monthly_col2 = st.columns(
    [2.1, 1],
    gap="large",
)


with monthly_col1:
    if monthly_trips.empty:
        st.warning(
            "No monthly trip data is available."
        )
    else:
        fig = monthly_trip_chart(
            monthly_trips
        )

        fig.update_layout(
            height=450,
            margin=dict(
                l=10,
                r=10,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


with monthly_col2:
    if (
        not monthly_trips.empty
        and "total_trips" in monthly_trips.columns
    ):
        monthly_copy = monthly_trips.copy()

        monthly_copy = monthly_copy.sort_values(
            "total_trips",
            ascending=False,
        )

        top_month = monthly_copy.iloc[0]

        bottom_month = monthly_copy.iloc[-1]

        top_month_name = top_month.get(
            "month",
            "N/A",
        )

        top_month_trips = safe_float(
            top_month.get(
                "total_trips",
                0,
            )
        )

        bottom_month_name = bottom_month.get(
            "month",
            "N/A",
        )

        bottom_month_trips = safe_float(
            bottom_month.get(
                "total_trips",
                0,
            )
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="small-label">
                    Seasonal demand signal
                </div>
                <div class="big-number">
                    {top_month_trips:,.0f}
                </div>
                <p>
                    trips in <strong>{top_month_name}</strong>,
                    the strongest month.
                </p>
                <hr>
                <p>
                    The lowest observed month was
                    <strong>{bottom_month_name}</strong>
                    with approximately
                    <strong>{bottom_month_trips:,.0f}</strong>
                    trips.
                </p>
                <p>
                    The gap between the strongest and weakest
                    months provides a direct measure of seasonal
                    demand variation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


hour_col, weekday_col = st.columns(
    2,
    gap="large",
)


with hour_col:
    st.subheader("🕐 Intraday demand")

    if hourly_trips.empty:
        st.warning(
            "No hourly trip data is available."
        )
    else:
        fig = hourly_trip_chart(
            hourly_trips
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=10,
                r=10,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


with weekday_col:
    st.subheader("📅 Weekly demand")

    if weekday_trips.empty:
        st.warning(
            "No weekday trip data is available."
        )
    else:
        fig = weekday_trip_chart(
            weekday_trips
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=10,
                r=10,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


st.divider()


st.markdown(
    """
    <div class="section-label">WEATHER EXPOSURE</div>
    <div class="section-title">How does weather change the financial picture?</div>
    <div class="section-description">
        Weather is treated as a demand and revenue condition,
        not simply as a descriptive label.
    </div>
    """,
    unsafe_allow_html=True,
)


weather_col1, weather_col2 = st.columns(
    [1.65, 1],
    gap="large",
)


with weather_col1:
    if revenue_impact.empty:
        st.warning(
            "No revenue/weather data is available."
        )
    else:
        fig = revenue_weather_chart(
            revenue_impact
        )

        fig.update_layout(
            height=470,
            margin=dict(
                l=10,
                r=10,
                t=60,
                b=20,
        ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


with weather_col2:
    dry = get_weather_revenue("Dry")
    rain = get_weather_revenue("Rain")
    light = get_weather_revenue(
        "Light precipitation"
    )

    if not dry.empty:
        dry_revenue = safe_float(
            dry.get(
                "avg_daily_gross_customer_charges_usd",
                0,
            )
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="small-label">
                    Clear-day benchmark
                </div>
                <div class="big-number">
                    {format_money(dry_revenue)}
                </div>
                <p>
                    average daily gross customer charges
                    during dry conditions.
                </p>
            """,
            unsafe_allow_html=True,
        )

        if not rain.empty:
            rain_revenue = safe_float(
                rain.get(
                    "avg_daily_gross_customer_charges_usd",
                    0,
                )
            )

            rain_difference = (
                dry_revenue
                - rain_revenue
            )

            rain_percentage = (
                rain_difference
                / dry_revenue
                * 100
                if dry_revenue
                else 0
            )

            st.markdown(
                f"""
                    <hr>
                    <div class="small-label">
                        Rain exposure
                    </div>
                    <p>
                        Rainy days generate approximately
                        <strong>{format_money(rain_difference)}</strong>
                        less gross customer charges per day
                        than dry days.
                    </p>
                    <p>
                        That represents approximately
                        <strong>{rain_percentage:.1f}%</strong>
                        lower average daily gross charges.
                    </p>
                """,
                unsafe_allow_html=True,
            )

        if not light.empty:
            light_revenue = safe_float(
                light.get(
                    "avg_daily_gross_customer_charges_usd",
                    0,
                )
            )

            light_difference = (
                light_revenue
                - dry_revenue
            )

            st.markdown(
                f"""
                    <hr>
                    <div class="small-label">
                        Light precipitation
                    </div>
                    <p>
                        Light precipitation changes average
                        daily gross charges by approximately
                        <strong>{format_money(abs(light_difference))}</strong>
                        relative to dry conditions.
                    </p>
                    <p>
                        This distinction matters because
                        precipitation does not automatically
                        translate into a major revenue decline.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


st.divider()


st.markdown(
    """
    <div class="section-label">EXECUTIVE TAKEAWAYS</div>
    <div class="section-title">What should leadership take away?</div>
    <div class="section-description">
        These observations summarize the strongest signals
        available from the current historical warehouse.
    </div>
    """,
    unsafe_allow_html=True,
)


takeaway1, takeaway2, takeaway3 = st.columns(
    3,
    gap="large",
)


with takeaway1:
    st.markdown(
        f"""
        <div class="insight-card">
            <h4>🚕 Demand concentration</h4>
            <p>
                The network processes approximately
                <strong>{total_trips:,.0f}</strong>
                annual taxi trips.
            </p>
            <p>
                Average demand is approximately
                <strong>{avg_daily_trips:,.0f}</strong>
                trips per day.
            </p>
            <p>
                This baseline provides the reference point
                for all operational and weather comparisons.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with takeaway2:
    if not rain.empty and not dry.empty:
        dry_demand = safe_float(
            dry.get(
                "avg_daily_trips",
                0,
            )
        )

        rain_demand = safe_float(
            rain.get(
                "avg_daily_trips",
                0,
            )
        )

        if dry_demand:
            rain_change = (
                rain_demand
                - dry_demand
            ) / dry_demand * 100
        else:
            rain_change = 0

        st.markdown(
            f"""
            <div class="insight-card">
                <h4>🌧️ Weather exposure</h4>
                <p>
                    Rainy conditions are associated with
                    approximately
                    <strong>{abs(rain_change):.1f}%</strong>
                    lower average daily taxi demand than
                    dry conditions.
                </p>
                <p>
                    The effect should be interpreted as a
                    historical association rather than proof
                    that rainfall alone caused the decline.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="insight-card">
                <h4>🌧️ Weather exposure</h4>
                <p>
                    Weather exposure could not be calculated
                    from the currently returned data.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


with takeaway3:
    if not peak_hour.empty:
        hour_value = peak_hour.get(
            "pickup_hour",
            peak_hour.get(
                "hour",
                "N/A",
            ),
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <h4>⏱️ Operating pressure</h4>
                <p>
                    The strongest observed hourly demand
                    occurs around
                    <strong>{hour_value}</strong>.
                </p>
                <p>
                    Concentrated demand periods provide a
                    practical starting point for capacity,
                    availability, and workforce planning.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.divider()


st.markdown(
    """
    <div class="section-label">WEATHER PERFORMANCE MATRIX</div>
    <div class="section-title">Demand and revenue by condition</div>
    <div class="section-description">
        Comparing volume, revenue, and tips together provides
        a more complete picture than looking at any single
        weather metric.
    </div>
    """,
    unsafe_allow_html=True,
)


if not revenue_impact.empty:

    matrix_columns = [
        column
        for column in [
            "weather_condition",
            "days_in_category",
            "avg_daily_trips",
            "avg_daily_gross_customer_charges_usd",
            "avg_daily_tips_usd",
            "avg_customer_charge_per_trip_usd",
        ]
        if column in revenue_impact.columns
    ]

    matrix = revenue_impact[
        matrix_columns
    ].copy()

    rename_map = {
        "weather_condition": "Weather",
        "days_in_category": "Days",
        "avg_daily_trips": "Avg daily trips",
        "avg_daily_gross_customer_charges_usd":
            "Avg daily gross charges",
        "avg_daily_tips_usd":
            "Avg daily tips",
        "avg_customer_charge_per_trip_usd":
            "Avg charge / trip",
    }

    matrix = matrix.rename(
        columns=rename_map
    )

    st.dataframe(
        matrix,
        use_container_width=True,
        hide_index=True,
    )


st.divider()


st.markdown(
    """
    <div class="section-label">DECISION SUPPORT</div>
    <div class="section-title">Executive watchpoints</div>
    <div class="section-description">
        The dashboard distinguishes what the current historical
        data can establish from capabilities that require additional
        data sources.
    </div>
    """,
    unsafe_allow_html=True,
)


watch1, watch2 = st.columns(
    2,
    gap="large",
)


with watch1:
    if not rain.empty and not dry.empty:
        rain_change = calculate_weather_percentage(
            "Rain",
            "avg_daily_trips",
        )

        if rain_change is not None and rain_change < 0:
            st.markdown(
                f"""
                <div class="status-watch">
                    <strong>Weather demand watch</strong><br>
                    Historical rain conditions are associated
                    with approximately
                    <strong>{abs(rain_change):.1f}%</strong>
                    lower average daily demand than dry
                    conditions.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="status-good">
                    <strong>Weather demand watch</strong><br>
                    No negative rain-demand signal was detected
                    from the available aggregate weather data.
                </div>
                """,
                unsafe_allow_html=True,
            )


with watch2:
    if not rain.empty and not dry.empty:
        revenue_change = calculate_weather_percentage(
            "Rain",
            "avg_daily_gross_customer_charges_usd",
        )

        if (
            revenue_change is not None
            and revenue_change < 0
        ):
            st.markdown(
                f"""
                <div class="status-watch">
                    <strong>Revenue exposure watch</strong><br>
                    Historical rainy days are associated with
                    approximately
                    <strong>{abs(revenue_change):.1f}%</strong>
                    lower average daily gross customer
                    charges than dry days.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="status-good">
                    <strong>Revenue exposure watch</strong><br>
                    No negative rainy-day revenue signal was
                    detected from the available aggregate data.
                </div>
                """,
                unsafe_allow_html=True,
            )


st.divider()


with st.expander(
    "ℹ️ What this dashboard can and cannot establish"
):

    st.markdown(
        """
        ### What the current warehouse supports

        This executive layer is built from historical 2021
        analytical tables containing:

        - Taxi trip demand
        - Monthly demand
        - Hourly demand
        - Weekday demand
        - Pickup-zone demand
        - Daily weather
        - Temperature
        - Precipitation
        - Snowfall
        - Wind
        - Weather-by-weekday demand
        - Weather-by-revenue relationships

        These datasets support historical descriptive and
        comparative analysis.

        ### What the dashboard does not claim

        The current system does not contain real-time vehicle
        positions, traffic sensors, public-transit telemetry,
        bike or scooter availability, EV battery telemetry,
        weather radar, surge pricing, or live incident feeds.

        Therefore this dashboard does not claim to provide:

        - Real-time congestion detection
        - Live fleet positioning
        - Subway overcrowding
        - Real-time transit delays
        - Current flooded intersections
        - Live surge pricing
        - EV charging optimization
        - Real-time emergency routing
        - Future climate forecasts

        Those capabilities would require additional data
        integrations.

        ### Analytical interpretation

        Weather comparisons should be interpreted as
        **historical associations**.

        A difference between rainy and dry days does not by
        itself prove that precipitation caused the entire
        difference in demand. Other factors can influence
        taxi activity, including seasonality, weekday,
        holidays, temperature, events, and broader changes
        in travel behavior.

        The purpose of this dashboard is therefore to provide
        a defensible historical decision-support baseline.
        """
    )


st.divider()


st.markdown(
    """
    <div class="section-label">DATA COVERAGE</div>
    <div class="section-title">Executive data foundation</div>
    """,
    unsafe_allow_html=True,
)


coverage = pd.DataFrame(
    {
        "Analytical capability": [
            "Annual taxi demand",
            "Daily taxi demand",
            "Monthly demand",
            "Hourly demand",
            "Weekday demand",
            "Pickup-zone demand",
            "Weather conditions",
            "Temperature",
            "Precipitation",
            "Snowfall",
            "Wind",
            "Weather × weekday",
            "Weather × revenue",
            "Real-time GPS",
            "Transit telemetry",
            "EV telemetry",
            "Micro-mobility telemetry",
            "Weather radar",
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
            "Future",
            "Future",
            "Future",
            "Future",
            "Future",
        ],
    }
)


st.dataframe(
    coverage,
    use_container_width=True,
    hide_index=True,
)


st.markdown(
    """
    <div class="footer-note">
        Urban Mobility Analytics • BigQuery • Python • Streamlit • Plotly
        <br>
        Historical analytical period: 2021
    </div>
    """,
    unsafe_allow_html=True,
)