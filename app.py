"""Urban Mobility Intelligence Command Center."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from data_loader import (
    load_hourly_trips,
    load_monthly_trips,
    load_pickup_zones,
    load_daily_weather,
    load_revenue_weather_impact,
    load_weekday_trips,
)

from metrics import (
    calculate_overview_metrics,
    get_peak_hour,
    get_peak_month,
    get_peak_weekday,
    get_top_pickup_zone,
)


st.set_page_config(
    page_title="Urban Mobility Intelligence",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATA
# ============================================================

@st.cache_data(show_spinner="Loading command center data...")
def load_command_center_data():
    monthly = load_monthly_trips()
    hourly = load_hourly_trips()
    weekday = load_weekday_trips()
    zones = load_pickup_zones()
    weather = load_daily_weather()
    revenue = load_revenue_weather_impact()

    return (
        monthly,
        hourly,
        weekday,
        zones,
        weather,
        revenue,
    )


(
    monthly_trips,
    hourly_trips,
    weekday_trips,
    pickup_zones,
    daily_weather,
    revenue_impact,
) = load_command_center_data()


# ============================================================
# SAFE HELPERS
# ============================================================

def numeric_value(
    dataframe: pd.DataFrame,
    column: str,
    default: float = 0.0,
) -> float:

    if dataframe is None:
        return default

    if dataframe.empty:
        return default

    if column not in dataframe.columns:
        return default

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )

    if values.dropna().empty:
        return default

    return float(values.sum())


def average_value(
    dataframe: pd.DataFrame,
    column: str,
    default: float = 0.0,
) -> float:

    if dataframe is None:
        return default

    if dataframe.empty:
        return default

    if column not in dataframe.columns:
        return default

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )

    if values.dropna().empty:
        return default

    return float(values.mean())


def row_value(
    row,
    column: str,
    default=None,
):
    if row is None:
        return default

    try:
        value = row.get(column, default)
    except AttributeError:
        return default

    return value


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


# ============================================================
# CALCULATE EXECUTIVE METRICS
# ============================================================

total_trips = numeric_value(
    monthly_trips,
    "total_trips",
)


avg_daily_trips = 0.0

if (
    daily_weather is not None
    and not daily_weather.empty
    and "total_trips" in daily_weather.columns
):

    avg_daily_trips = average_value(
        daily_weather,
        "total_trips",
    )

elif (
    monthly_trips is not None
    and not monthly_trips.empty
):

    avg_daily_trips = (
        total_trips / 365
        if total_trips > 0
        else 0
    )


overview = calculate_overview_metrics(
    daily_weather=None,
    revenue_impact=revenue_impact,
)


avg_daily_gross_charges = float(
    overview.get(
        "avg_daily_gross_charges_usd",
        0,
    )
)


avg_daily_tips = float(
    overview.get(
        "avg_daily_tips_usd",
        0,
    )
)


# ============================================================
# PEAK METRICS
# ============================================================

peak_month = get_peak_month(
    monthly_trips
)


peak_hour = get_peak_hour(
    hourly_trips
)


peak_weekday = get_peak_weekday(
    weekday_trips
)


top_zone = get_top_pickup_zone(
    pickup_zones
)


# ============================================================
# PEAK MONTH
# ============================================================

peak_month_name = row_value(
    peak_month,
    "month",
    "N/A",
)


peak_month_trips = row_value(
    peak_month,
    "total_trips",
    0,
)


# ============================================================
# PEAK HOUR
# ============================================================

if "pickup_hour" in peak_hour.index:

    peak_hour_value = row_value(
        peak_hour,
        "pickup_hour",
        "N/A",
    )

else:

    peak_hour_value = row_value(
        peak_hour,
        "hour",
        "N/A",
    )


if "avg_trips" in peak_hour.index:

    peak_hour_trips = row_value(
        peak_hour,
        "avg_trips",
        0,
    )

else:

    peak_hour_trips = row_value(
        peak_hour,
        "total_trips",
        0,
    )


# ============================================================
# PEAK WEEKDAY
# ============================================================

peak_weekday_name = row_value(
    peak_weekday,
    "day_of_week",
    "N/A",
)


if "avg_daily_trips" in peak_weekday.index:

    peak_weekday_trips = row_value(
        peak_weekday,
        "avg_daily_trips",
        0,
    )

else:

    peak_weekday_trips = row_value(
        peak_weekday,
        "total_trips",
        0,
    )


# ============================================================
# TOP ZONE
# ============================================================

top_zone_name = row_value(
    top_zone,
    "pickup_zone",
    "N/A",
)


top_zone_borough = row_value(
    top_zone,
    "borough",
    "N/A",
)


top_zone_trips = row_value(
    top_zone,
    "total_trips",
    0,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🚕 Command Center")

    st.caption(
        "Urban Mobility Intelligence"
    )

    st.divider()

    st.markdown(
        "### Navigation"
    )

    st.markdown(
        """
        **🏠 Command Center**

        Use the pages below for deeper analysis:

        **🚕 Executive Dashboard**  
        Demand, operating periods, and revenue.

        **🌦️ Weather & Geography**  
        Weather exposure and spatial patterns.

        **🧠 BI Questions**  
        Business questions, statistical analysis,
        and decision support.
        """
    )

    st.divider()

    st.markdown(
        "### Data environment"
    )

    st.caption(
        "Historical analytical environment"
    )

    st.caption(
        "Period: 2021"
    )

    st.caption(
        "Warehouse: BigQuery"
    )

    st.caption(
        "Application: Streamlit"
    )


# ============================================================
# HERO
# ============================================================

st.title(
    "🚕 Urban Mobility Intelligence"
)

st.markdown(
    """
    ### Command Center

    A high-level operating environment for understanding
    urban taxi demand, operating patterns, weather exposure,
    geographic concentration, and revenue performance.
    """
)

st.info(
    "Historical 2021 analytical environment • "
    "BigQuery powered • Decision-support ready"
)


# ============================================================
# EXECUTIVE PULSE
# ============================================================

st.divider()

st.header(
    "📊 Executive Pulse"
)

st.caption(
    "City-wide mobility snapshot"
)

st.write(
    "The most important indicators currently available "
    "from the analytical warehouse."
)


kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.metric(
        label="Total Trips",
        value=format_number(
            total_trips
        ),
    )

    st.caption(
        "Historical 2021 demand"
    )


with kpi2:

    st.metric(
        label="Average Daily Demand",
        value=format_number(
            avg_daily_trips
        ),
    )

    st.caption(
        "Average trips per day"
    )


with kpi3:

    st.metric(
        label="Avg Daily Gross Charges",
        value=format_currency(
            avg_daily_gross_charges
        ),
    )

    st.caption(
        "Customer gross charges"
    )


with kpi4:

    st.metric(
        label="Avg Daily Tips",
        value=format_currency(
            avg_daily_tips
        ),
    )

    st.caption(
        "Historical tip activity"
    )


# ============================================================
# OPERATING PULSE
# ============================================================

st.divider()

st.header(
    "📈 Operating Pulse"
)

st.caption(
    "When and where demand concentrates"
)

st.write(
    "Identify the periods and locations that matter most "
    "for mobility operations."
)


op1, op2, op3 = st.columns(3)


with op1:

    st.metric(
        "Peak Month",
        str(peak_month_name),
        f"{float(peak_month_trips):,.0f} trips",
    )


with op2:

    st.metric(
        "Peak Hour",
        str(peak_hour_value),
        f"{float(peak_hour_trips):,.0f} trips",
    )


with op3:

    st.metric(
        "Peak Weekday",
        str(peak_weekday_name),
        f"{float(peak_weekday_trips):,.0f} trips",
    )


# ============================================================
# NETWORK SCALE
# ============================================================

st.markdown(
    "### Network Scale"
)


scale1, scale2, scale3, scale4 = st.columns(4)


with scale1:

    zone_count = (
        pickup_zones["pickup_zone"]
        .nunique()
        if (
            not pickup_zones.empty
            and "pickup_zone"
            in pickup_zones.columns
        )
        else len(pickup_zones)
    )

    st.metric(
        "Pickup Zones",
        f"{zone_count:,}",
    )


with scale2:

    weather_days = (
        len(daily_weather)
        if daily_weather is not None
        else 0
    )

    st.metric(
        "Weather Days",
        f"{weather_days:,}",
    )


with scale3:

    month_count = (
        len(monthly_trips)
        if monthly_trips is not None
        else 0
    )

    st.metric(
        "Months",
        f"{month_count:,}",
    )


with scale4:

    hour_count = (
        len(hourly_trips)
        if hourly_trips is not None
        else 0
    )

    st.metric(
        "Hourly Periods",
        f"{hour_count:,}",
    )


# ============================================================
# DEMAND INTELLIGENCE
# ============================================================

st.divider()

st.header(
    "🚕 Demand Intelligence"
)

st.caption(
    "How mobility demand moves through the year"
)

st.write(
    "Monthly demand provides the high-level operating "
    "rhythm of the historical taxi network."
)


monthly_tab, hourly_tab, weekday_tab = st.tabs(
    [
        "📅 Monthly",
        "🕐 Hourly",
        "📆 Weekday",
    ]
)


with monthly_tab:

    if monthly_trips.empty:

        st.warning(
            "Monthly demand data is unavailable."
        )

    else:

        import plotly.express as px

        monthly_plot = monthly_trips.copy()

        month_column = (
            "month"
            if "month" in monthly_plot.columns
            else None
        )

        trips_column = (
            "total_trips"
            if "total_trips"
            in monthly_plot.columns
            else None
        )

        if (
            month_column is not None
            and trips_column is not None
        ):

            fig = px.bar(
                monthly_plot,
                x=month_column,
                y=trips_column,
                title="Monthly Taxi Demand",
                labels={
                    month_column: "Month",
                    trips_column: "Total Trips",
                },
            )

            fig.update_layout(
                height=450,
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20,
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )


with hourly_tab:

    if hourly_trips.empty:

        st.warning(
            "Hourly demand data is unavailable."
        )

    else:

        import plotly.express as px

        hour_column = (
            "pickup_hour"
            if "pickup_hour"
            in hourly_trips.columns
            else "hour"
        )

        trip_column = (
            "avg_trips"
            if "avg_trips"
            in hourly_trips.columns
            else "total_trips"
        )

        if (
            hour_column in hourly_trips.columns
            and trip_column in hourly_trips.columns
        ):

            fig = px.line(
                hourly_trips,
                x=hour_column,
                y=trip_column,
                markers=True,
                title="Hourly Taxi Demand",
                labels={
                    hour_column: "Hour",
                    trip_column: "Trips",
                },
            )

            fig.update_layout(
                height=450,
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20,
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )


with weekday_tab:

    if weekday_trips.empty:

        st.warning(
            "Weekday demand data is unavailable."
        )

    else:

        import plotly.express as px

        day_column = (
            "day_of_week"
            if "day_of_week"
            in weekday_trips.columns
            else None
        )

        trip_column = (
            "avg_daily_trips"
            if "avg_daily_trips"
            in weekday_trips.columns
            else "total_trips"
        )

        if (
            day_column is not None
            and trip_column in weekday_trips.columns
        ):

            fig = px.bar(
                weekday_trips,
                x=day_column,
                y=trip_column,
                title="Weekday Taxi Demand",
                labels={
                    day_column: "Day",
                    trip_column: "Trips",
                },
            )

            fig.update_layout(
                height=450,
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20,
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )


# ============================================================
# WEATHER INTELLIGENCE
# ============================================================

st.divider()

st.header(
    "🌦️ Weather Intelligence"
)

st.caption(
    "Weather exposure and mobility behavior"
)

st.write(
    "Historical weather categories provide context for "
    "understanding demand and revenue volatility."
)


if revenue_impact.empty:

    st.warning(
        "Revenue/weather data is unavailable."
    )

else:

    import plotly.express as px

    weather_plot = revenue_impact.copy()

    weather_column = (
        "weather_condition"
        if "weather_condition"
        in weather_plot.columns
        else None
    )

    revenue_column = (
        "avg_daily_gross_customer_charges_usd"
        if (
            "avg_daily_gross_customer_charges_usd"
            in weather_plot.columns
        )
        else None
    )

    if (
        weather_column is not None
        and revenue_column is not None
    ):

        fig = px.bar(
            weather_plot,
            x=weather_column,
            y=revenue_column,
            title="Average Daily Gross Charges by Weather",
            labels={
                weather_column: "Weather",
                revenue_column: "Average Daily Gross Charges",
            },
        )

        fig.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# ============================================================
# SPATIAL INTELLIGENCE
# ============================================================

st.divider()

st.header(
    "📍 Spatial Intelligence"
)

st.caption(
    "Where mobility demand concentrates"
)

st.write(
    "Pickup-zone concentration provides an operational "
    "starting point for capacity planning and future "
    "spatial resilience analysis."
)


spatial_left, spatial_right = st.columns(
    [1, 2]
)


with spatial_left:

    st.metric(
        "Highest-volume Pickup Zone",
        str(top_zone_name),
    )

    st.write(
        f"**Borough:** {top_zone_borough}"
    )

    st.write(
        f"**Historical trips:** "
        f"{float(top_zone_trips):,.0f}"
    )


with spatial_right:

    if (
        not pickup_zones.empty
        and "total_trips"
        in pickup_zones.columns
        and "pickup_zone"
        in pickup_zones.columns
    ):

        import plotly.express as px

        top_zones = (
            pickup_zones
            .sort_values(
                "total_trips",
                ascending=False,
            )
            .head(15)
            .sort_values(
                "total_trips",
                ascending=True,
            )
        )

        fig = px.bar(
            top_zones,
            x="total_trips",
            y="pickup_zone",
            orientation="h",
            title="Top Pickup Zones",
            labels={
                "total_trips": "Total Trips",
                "pickup_zone": "Pickup Zone",
            },
        )

        fig.update_layout(
            height=500,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# ============================================================
# ANALYTICAL PLATFORM
# ============================================================

st.divider()

st.header(
    "🧠 Analytical Platform"
)

st.caption(
    "Move from observation to decision"
)

st.write(
    "Each analytical page answers a different class "
    "of mobility intelligence question."
)


platform1, platform2, platform3 = st.columns(3)


with platform1:

    st.subheader(
        "🚕 Executive Dashboard"
    )

    st.write(
        """
        Monitor the major demand, revenue,
        hourly, monthly, and weekday operating
        patterns across the historical network.

        Designed for fast executive interpretation.
        """
    )


with platform2:

    st.subheader(
        "🌦️ Weather & Geography"
    )

    st.write(
        """
        Explore weather conditions, geographic
        demand concentration, temperature,
        precipitation, snowfall, and wind effects.

        Designed for environmental and spatial analysis.
        """
    )


with platform3:

    st.subheader(
        "🧠 BI Questions"
    )

    st.write(
        """
        Move beyond charts into explicit business
        questions, statistical relationships,
        operational interpretation, and scenario
        analysis.

        Designed for decision support.
        """
    )


# ============================================================
# DATA FOUNDATION
# ============================================================

st.divider()

st.header(
    "🧩 Data Foundation"
)

st.caption(
    "Analytical coverage"
)


foundation = pd.DataFrame(
    {
        "Capability": [
            "Taxi demand",
            "Monthly demand",
            "Hourly demand",
            "Weekday demand",
            "Pickup-zone demand",
            "Daily weather",
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
            "Future",
            "Future",
            "Future",
            "Future",
            "Future",
        ],
    }
)


st.dataframe(
    foundation,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# INTERPRETATION
# ============================================================

with st.expander(
    "ℹ️ Analytical scope and interpretation"
):

    st.markdown(
        """
        ### What this command center represents

        This application is a historical urban mobility
        intelligence environment built around the available
        2021 analytical warehouse.

        The Command Center intentionally separates:

        **Observed facts**

        Values calculated directly from the analytical
        datasets.

        **Analytical interpretation**

        Conclusions derived from relationships in the
        available data.

        **Future capabilities**

        Questions that require additional datasets such as
        real-time GPS, transit telemetry, weather radar,
        EV telemetry, or micro-mobility data.

        ### Current analytical foundation

        The current environment contains:

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
        - Weather × weekday analysis
        - Weather × revenue analysis

        ### Why the distinction matters

        A business intelligence platform should not manufacture
        answers for questions that the underlying data cannot
        support.

        The command center therefore presents calculated
        metrics as facts and reserves deeper interpretation
        for the analytical pages.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🚕 Urban Mobility Analytics • "
    "Historical period: 2021 • "
    "Data warehouse: BigQuery • "
    "Application: Streamlit • "
    "Visualization: Plotly"
)