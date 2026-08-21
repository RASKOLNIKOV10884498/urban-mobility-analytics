"""
Urban Mobility Analytics
Statistical Analysis Engine

Purpose
-------
Runs reproducible descriptive and inferential statistical analysis
against the analytical datasets loaded from BigQuery.

Analysis included
-----------------
1. Dataset loading
2. Dataset validation
3. Pearson correlation
4. Spearman correlation
5. Simple linear regression
6. Multivariate weather regression
7. Regression confidence intervals
8. Residual diagnostics
9. Multicollinearity / VIF
10. Weather category effect sizes
11. One-way ANOVA
12. Tukey HSD post-hoc comparisons
13. Revenue/weather effects
14. Monthly demand variability
15. Hourly demand concentration
16. Weekday demand variability
17. Spatial demand concentration
18. Individual weather-variable analysis
19. 95% confidence interval for daily demand
20. Consolidated statistical findings

Important
---------
These analyses identify statistical associations in the available
historical 2021 data. They do not, by themselves, establish causation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.outliers_influence import variance_inflation_factor


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "analysis"
    / "outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# Make the project root importable when this script is executed directly.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ============================================================================
# DATA LOADER IMPORT
# ============================================================================

try:

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
        load_revenue_weather_daily,
    )

except ImportError as exc:

    raise ImportError(
        "\nCould not import the project's data_loader module.\n\n"
        "Make sure data_loader.py is available from the project root:\n"
        f"{PROJECT_ROOT}\n\n"
        "Original error:\n"
        f"{exc}"
    ) from exc


# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

TARGET_VARIABLE = "total_trips"

WEATHER_VARIABLES = [
    "avg_temperature_f",
    "precipitation_inches",
    "snowfall_inches",
    "max_wind_speed_mph",
]

ALPHA = 0.05

# Strength thresholds are intentionally conservative.
CORRELATION_THRESHOLDS = {
    "negligible": 0.10,
    "weak": 0.30,
    "moderate": 0.50,
    "strong": 0.70,
}


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def section(title: str) -> None:
    """Print a clearly separated analysis section."""

    print()
    print("=" * 88)
    print(title)
    print("=" * 88)


def fmt_pvalue(
    value: float | int | np.floating,
) -> str:
    """Format a p-value for readable terminal output."""

    if value is None:
        return "not available"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "not available"

    if not np.isfinite(value):
        return "not available"

    if value < 0.000001:
        return "< 0.000001"

    return f"{value:.6f}"


def significance_label(
    p_value: float | int | np.floating,
) -> str:
    """Return an interpretable significance label."""

    try:
        p_value = float(p_value)
    except (TypeError, ValueError):
        return "not available"

    if not np.isfinite(p_value):
        return "not available"

    if p_value < 0.001:
        return "highly significant"

    if p_value < 0.05:
        return "statistically significant"

    return "not statistically significant"


def correlation_strength(
    coefficient: float | int | np.floating,
) -> str:
    """Classify absolute correlation magnitude."""

    try:
        coefficient = abs(float(coefficient))
    except (TypeError, ValueError):
        return "not available"

    if not np.isfinite(coefficient):
        return "not available"

    if coefficient < 0.10:
        return "negligible"

    if coefficient < 0.30:
        return "weak"

    if coefficient < 0.50:
        return "moderate"

    if coefficient < 0.70:
        return "strong"

    return "very strong"


def numeric_series(
    dataframe: pd.DataFrame,
    column: str,
) -> pd.Series:
    """Safely return a numeric series."""

    if dataframe is None:
        return pd.Series(
            dtype=float
        )

    if column not in dataframe.columns:
        return pd.Series(
            dtype=float
        )

    return pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_dataset(
    dataset_name: str,
    dataframe: pd.DataFrame,
    required_columns: Iterable[str],
) -> bool:
    """Validate that a dataset exists and contains required columns."""

    required_columns = list(
        required_columns
    )

    if dataframe is None:

        print(
            f"WARNING: {dataset_name} returned None."
        )

        return False

    if dataframe.empty:

        print(
            f"WARNING: {dataset_name} is empty."
        )

        return False

    missing = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing:

        print(
            f"WARNING: {dataset_name} missing columns: "
            f"{', '.join(missing)}"
        )

        return False

    return True


def validate_all_datasets(
    monthly_trips: pd.DataFrame,
    hourly_trips: pd.DataFrame,
    weekday_trips: pd.DataFrame,
    zones: pd.DataFrame,
    daily_weather: pd.DataFrame,
    weather_impact: pd.DataFrame,
    revenue_weather: pd.DataFrame,
) -> pd.DataFrame:
    """Create a validation report for all analytical datasets."""

    section(
        "2. DATASET VALIDATION"
    )

    requirements = {
        "monthly": [
            "total_trips",
        ],
        "hourly": [
            "pickup_hour",
            "total_trips",
        ],
        "weekday": [
            "total_trips",
        ],
        "zones": [
            "total_trips",
        ],
        "daily_weather": [
            "weather_condition",
            "total_trips",
            *WEATHER_VARIABLES,
        ],
        "weather_impact": [
            "weather_condition",
            "total_trips",
        ],
        "revenue_weather": [
            "weather_condition",
            "gross_customer_charges_usd",
        ],
    }

    datasets = {
        "monthly": monthly_trips,
        "hourly": hourly_trips,
        "weekday": weekday_trips,
        "zones": zones,
        "daily_weather": daily_weather,
        "weather_impact": weather_impact,
        "revenue_weather": revenue_weather,
    }

    records = []

    for name, dataframe in datasets.items():

        required = requirements[name]

        valid = validate_dataset(
            name,
            dataframe,
            required,
        )

        records.append(
            {
                "dataset": name,
                "rows": (
                    int(len(dataframe))
                    if dataframe is not None
                    else 0
                ),
                "columns": (
                    int(len(dataframe.columns))
                    if dataframe is not None
                    else 0
                ),
                "valid": valid,
            }
        )

    validation = pd.DataFrame(
        records
    )

    print(
        validation.to_string(
            index=False
        )
    )

    validation.to_csv(
        OUTPUT_DIR
        / "dataset_validation.csv",
        index=False,
    )

    return validation


# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

def calculate_weather_correlations(
    daily_weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate both Pearson and Spearman relationships between
    weather variables and daily trips.
    """

    section(
        "3. WEATHER → DEMAND CORRELATION"
    )

    required = [
        TARGET_VARIABLE,
        *WEATHER_VARIABLES,
    ]

    if not validate_dataset(
        "daily_weather",
        daily_weather,
        required,
    ):

        return pd.DataFrame()

    records = []

    for variable in WEATHER_VARIABLES:

        dataframe = daily_weather[
            [
                variable,
                TARGET_VARIABLE,
            ]
        ].copy()

        dataframe[variable] = pd.to_numeric(
            dataframe[variable],
            errors="coerce",
        )

        dataframe[TARGET_VARIABLE] = pd.to_numeric(
            dataframe[TARGET_VARIABLE],
            errors="coerce",
        )

        dataframe = dataframe.dropna()

        if len(dataframe) < 3:

            print(
                f"{variable}: insufficient observations."
            )

            continue

        x = dataframe[variable]
        y = dataframe[TARGET_VARIABLE]

        try:

            pearson_r, pearson_p = (
                stats.pearsonr(
                    x,
                    y,
                )
            )

        except Exception:

            pearson_r = np.nan
            pearson_p = np.nan

        try:

            spearman_rho, spearman_p = (
                stats.spearmanr(
                    x,
                    y,
                )
            )

        except Exception:

            spearman_rho = np.nan
            spearman_p = np.nan

        print()
        print(
            f"{variable} → {TARGET_VARIABLE}"
        )

        print(
            f"  n = {len(dataframe)}"
        )

        print(
            f"  Pearson r = "
            f"{pearson_r:.4f}"
        )

        print(
            f"  Pearson strength = "
            f"{correlation_strength(pearson_r)}"
        )

        print(
            f"  Pearson p-value = "
            f"{fmt_pvalue(pearson_p)}"
        )

        print(
            f"  Pearson result = "
            f"{significance_label(pearson_p)}"
        )

        print(
            f"  Spearman rho = "
            f"{spearman_rho:.4f}"
        )

        print(
            f"  Spearman strength = "
            f"{correlation_strength(spearman_rho)}"
        )

        print(
            f"  Spearman p-value = "
            f"{fmt_pvalue(spearman_p)}"
        )

        print(
            f"  Spearman result = "
            f"{significance_label(spearman_p)}"
        )

        records.append(
            {
                "variable": variable,
                "target": TARGET_VARIABLE,
                "n": int(len(dataframe)),
                "pearson_r": float(pearson_r),
                "pearson_p_value": float(pearson_p),
                "pearson_strength": correlation_strength(
                    pearson_r
                ),
                "pearson_significance": significance_label(
                    pearson_p
                ),
                "spearman_rho": float(spearman_rho),
                "spearman_p_value": float(spearman_p),
                "spearman_strength": correlation_strength(
                    spearman_rho
                ),
                "spearman_significance": significance_label(
                    spearman_p
                ),
            }
        )

    result = pd.DataFrame(
        records
    )

    output_path = (
        OUTPUT_DIR
        / "weather_correlations.csv"
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved: {output_path}"
    )

    return result


# ============================================================================
# SIMPLE LINEAR REGRESSION
# ============================================================================

def calculate_weather_regressions(
    daily_weather: pd.DataFrame,
) -> pd.DataFrame:
    """Run one-variable OLS models for each weather predictor."""

    section(
        "4. WEATHER → DEMAND REGRESSION"
    )

    required = [
        TARGET_VARIABLE,
        *WEATHER_VARIABLES,
    ]

    if not validate_dataset(
        "daily_weather",
        daily_weather,
        required,
    ):

        return pd.DataFrame()

    records = []

    for variable in WEATHER_VARIABLES:

        dataframe = daily_weather[
            [
                variable,
                TARGET_VARIABLE,
            ]
        ].copy()

        dataframe[variable] = pd.to_numeric(
            dataframe[variable],
            errors="coerce",
        )

        dataframe[TARGET_VARIABLE] = pd.to_numeric(
            dataframe[TARGET_VARIABLE],
            errors="coerce",
        )

        dataframe = dataframe.dropna()

        if len(dataframe) < 3:
            continue

        x = sm.add_constant(
            dataframe[variable],
            has_constant="add",
        )

        y = dataframe[TARGET_VARIABLE]

        try:

            model = sm.OLS(
                y,
                x,
            ).fit()

            coefficient = float(
                model.params[variable]
            )

            coefficient_p = float(
                model.pvalues[variable]
            )

            ci = model.conf_int()

            ci_lower = float(
                ci.loc[
                    variable,
                    0,
                ]
            )

            ci_upper = float(
                ci.loc[
                    variable,
                    1,
                ]
            )

            records.append(
                {
                    "x": variable,
                    "y": TARGET_VARIABLE,
                    "n": int(len(dataframe)),
                    "r_squared": float(
                        model.rsquared
                    ),
                    "adjusted_r_squared": float(
                        model.rsquared_adj
                    ),
                    "coefficient": coefficient,
                    "coefficient_p_value": coefficient_p,
                    "coefficient_ci_lower": ci_lower,
                    "coefficient_ci_upper": ci_upper,
                }
            )

            print(
                f"{variable}: "
                f"coefficient={coefficient:.4f}, "
                f"R²={model.rsquared:.4f}, "
                f"adjusted R²={model.rsquared_adj:.4f}, "
                f"p={fmt_pvalue(coefficient_p)}"
            )

        except Exception as exc:

            print(
                f"{variable}: regression failed: {exc}"
            )

    result = pd.DataFrame(
        records
    )

    output_path = (
        OUTPUT_DIR
        / "weather_regressions.csv"
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved: {output_path}"
    )

    return result


# ============================================================================
# MULTIVARIATE WEATHER REGRESSION
# ============================================================================

def run_multivariate_weather_regression(
    daily_weather: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Estimate the joint relationship between weather variables
    and daily demand.
    """

    section(
        "5. MULTIVARIATE WEATHER → DEMAND REGRESSION"
    )

    required = [
        TARGET_VARIABLE,
        *WEATHER_VARIABLES,
    ]

    if not validate_dataset(
        "daily_weather",
        daily_weather,
        required,
    ):

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )

    dataframe = daily_weather[
        required
    ].copy()

    for column in required:

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe = dataframe.dropna()

    print(
        f"Complete observations used: "
        f"{len(dataframe)}"
    )

    if len(dataframe) <= len(
        WEATHER_VARIABLES
    ) + 1:

        print(
            "Insufficient observations for multivariate regression."
        )

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )

    formula = (
        "total_trips ~ "
        "avg_temperature_f + "
        "precipitation_inches + "
        "snowfall_inches + "
        "max_wind_speed_mph"
    )

    try:

        model = smf.ols(
            formula=formula,
            data=dataframe,
        ).fit()

    except Exception as exc:

        print(
            f"Multivariate regression failed: {exc}"
        )

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )

    coefficients = []

    confidence_intervals = model.conf_int()

    for variable in model.params.index:

        coefficient = float(
            model.params[variable]
        )

        p_value = float(
            model.pvalues[variable]
        )

        standard_error = float(
            model.bse[variable]
        )

        t_statistic = float(
            model.tvalues[variable]
        )

        ci_lower = float(
            confidence_intervals.loc[
                variable,
                0,
            ]
        )

        ci_upper = float(
            confidence_intervals.loc[
                variable,
                1,
            ]
        )

        if variable == "const":

            direction = (
                "positive"
                if coefficient > 0
                else "negative"
                if coefficient < 0
                else "neutral"
            )

        else:

            direction = (
                "positive"
                if coefficient > 0
                else "negative"
                if coefficient < 0
                else "neutral"
            )

        coefficients.append(
            {
                "variable": variable,
                "coefficient": coefficient,
                "standard_error": standard_error,
                "t_statistic": t_statistic,
                "p_value": p_value,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "significance": significance_label(
                    p_value
                ),
                "direction": direction,
            }
        )

    coefficients = pd.DataFrame(
        coefficients
    )

    model_summary = pd.DataFrame(
        [
            {
                "observations": int(
                    model.nobs
                ),
                "r_squared": float(
                    model.rsquared
                ),
                "adjusted_r_squared": float(
                    model.rsquared_adj
                ),
                "f_statistic": float(
                    model.fvalue
                ),
                "model_p_value": float(
                    model.f_pvalue
                ),
                "model_significance": significance_label(
                    model.f_pvalue
                ),
            }
        ]
    )

    fitted = model.fittedvalues
    residuals = model.resid
    y = dataframe[TARGET_VARIABLE]

    residual_mean = float(
        residuals.mean()
    )

    residual_std = float(
        residuals.std(
            ddof=1
        )
    )

    residual_skewness = float(
        stats.skew(
            residuals
        )
    )

    residual_kurtosis = float(
        stats.kurtosis(
            residuals
        )
    )

    shapiro_sample = residuals

    if len(shapiro_sample) > 5000:

        shapiro_sample = (
            shapiro_sample.sample(
                5000,
                random_state=42,
            )
        )

    try:

        shapiro_stat, shapiro_p = (
            stats.shapiro(
                shapiro_sample
            )
        )

    except Exception:

        shapiro_stat = np.nan
        shapiro_p = np.nan

    diagnostics = pd.DataFrame(
        [
            {
                "observations": int(
                    len(residuals)
                ),
                "residual_mean": residual_mean,
                "residual_std": residual_std,
                "residual_skewness": residual_skewness,
                "residual_kurtosis": residual_kurtosis,
                "shapiro_statistic": (
                    float(shapiro_stat)
                    if np.isfinite(
                        shapiro_stat
                    )
                    else np.nan
                ),
                "shapiro_p_value": (
                    float(shapiro_p)
                    if np.isfinite(
                        shapiro_p
                    )
                    else np.nan
                ),
                "residual_normality_result": (
                    significance_label(
                        shapiro_p
                    )
                    if np.isfinite(
                        shapiro_p
                    )
                    else "not available"
                ),
                "mean_absolute_error": float(
                    np.mean(
                        np.abs(
                            y - fitted
                        )
                    )
                ),
                "root_mean_squared_error": float(
                    np.sqrt(
                        np.mean(
                            np.square(
                                y - fitted
                            )
                        )
                    )
                ),
            }
        ]
    )

    print()
    print(
        "Model formula:"
    )

    print(
        formula
    )

    print()
    print(
        f"R² = "
        f"{model.rsquared:.4f}"
    )

    print(
        f"Adjusted R² = "
        f"{model.rsquared_adj:.4f}"
    )

    print(
        f"F-statistic = "
        f"{model.fvalue:.4f}"
    )

    print(
        f"Model p-value = "
        f"{fmt_pvalue(model.f_pvalue)}"
    )

    print(
        f"Model significance = "
        f"{significance_label(model.f_pvalue)}"
    )

    print()
    print(
        coefficients.to_string(
            index=False
        )
    )

    print()
    print(
        "Residual diagnostics:"
    )

    print(
        diagnostics.to_string(
            index=False
        )
    )

    coefficients.to_csv(
        OUTPUT_DIR
        / "multivariate_weather_coefficients.csv",
        index=False,
    )

    model_summary.to_csv(
        OUTPUT_DIR
        / "multivariate_weather_model.csv",
        index=False,
    )

    diagnostics.to_csv(
        OUTPUT_DIR
        / "multivariate_weather_diagnostics.csv",
        index=False,
    )

    print()
    print(
        "Saved:"
    )

    print(
        f"  {OUTPUT_DIR / 'multivariate_weather_coefficients.csv'}"
    )

    print(
        f"  {OUTPUT_DIR / 'multivariate_weather_model.csv'}"
    )

    print(
        f"  {OUTPUT_DIR / 'multivariate_weather_diagnostics.csv'}"
    )

    return (
        coefficients,
        model_summary,
        diagnostics,
    )


# ============================================================================
# VARIANCE INFLATION FACTOR
# ============================================================================

def calculate_vif(
    daily_weather: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "6. MULTICOLLINEARITY CHECK"
    )

    required = WEATHER_VARIABLES

    if not validate_dataset(
        "daily_weather",
        daily_weather,
        required,
    ):

        return pd.DataFrame()

    vif_data = daily_weather[
        required
    ].copy()

    for column in required:

        vif_data[column] = pd.to_numeric(
            vif_data[column],
            errors="coerce",
        )

    vif_data = vif_data.dropna()

    if len(vif_data) <= len(
        WEATHER_VARIABLES
    ):

        print(
            "Insufficient observations for VIF."
        )

        return pd.DataFrame()

    x = sm.add_constant(
        vif_data,
        has_constant="add",
    )

    records = []

    for index, column in enumerate(
        x.columns
    ):

        if column == "const":
            continue

        try:

            vif_value = variance_inflation_factor(
                x.values,
                index,
            )

        except Exception:

            vif_value = np.nan

        if not np.isfinite(
            vif_value
        ):

            interpretation = (
                "not available"
            )

        elif vif_value < 5:

            interpretation = (
                "acceptable"
            )

        elif vif_value < 10:

            interpretation = (
                "elevated"
            )

        else:

            interpretation = (
                "high multicollinearity"
            )

        records.append(
            {
                "variable": column,
                "vif": float(vif_value),
                "interpretation": interpretation,
            }
        )

    result = pd.DataFrame(
        records
    )

    print(
        result.to_string(
            index=False
        )
    )

    result.to_csv(
        OUTPUT_DIR
        / "weather_vif.csv",
        index=False,
    )

    print(
        f"Saved: "
        f"{OUTPUT_DIR / 'weather_vif.csv'}"
    )

    return result


# ============================================================================
# WEATHER CATEGORY EFFECTS
# ============================================================================

def calculate_weather_effect_sizes(
    daily_weather: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "7. WEATHER CATEGORY EFFECTS"
    )

    required = [
        "weather_condition",
        TARGET_VARIABLE,
    ]

    if not validate_dataset(
        "daily_weather",
        daily_weather,
        required,
    ):

        return pd.DataFrame()

    dataframe = daily_weather[
        required
    ].copy()

    dataframe[
        TARGET_VARIABLE
    ] = pd.to_numeric(
        dataframe[
            TARGET_VARIABLE
        ],
        errors="coerce",
    )

    dataframe = dataframe.dropna()

    grouped = (
        dataframe
        .groupby(
            "weather_condition"
        )[TARGET_VARIABLE]
        .agg(
            [
                "count",
                "mean",
                "std",
            ]
        )
        .reset_index()
    )

    dry_rows = grouped[
        grouped[
            "weather_condition"
        ].eq("Dry")
    ]

    if dry_rows.empty:

        baseline = float(
            grouped["mean"].iloc[0]
        )

        baseline_name = str(
            grouped[
                "weather_condition"
            ].iloc[0]
        )

    else:

        baseline = float(
            dry_rows[
                "mean"
            ].iloc[0]
        )

        baseline_name = "Dry"

    grouped[
        "difference_vs_baseline"
    ] = (
        grouped["mean"]
        - baseline
    )

    if baseline != 0:

        grouped[
            "percent_change_vs_baseline"
        ] = (
            grouped[
                "difference_vs_baseline"
            ]
            / baseline
            * 100
        )

    else:

        grouped[
            "percent_change_vs_baseline"
        ] = np.nan

    grouped[
        "baseline_category"
    ] = baseline_name

    print(
        grouped.to_string(
            index=False
        )
    )

    output_path = (
        OUTPUT_DIR
        / "weather_effect_sizes.csv"
    )

    grouped.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved: {output_path}"
    )

    return grouped


# ============================================================================
# ANOVA
# ============================================================================

def run_weather_anova(
    daily_weather: pd.DataFrame,
) -> dict[str, float] | None:

    section(
        "8. WEATHER ANOVA"
    )

    required = [
        "weather_condition",
        TARGET_VARIABLE,
    ]

    if not validate_dataset(
        "daily_weather",
        daily_weather,
        required,
    ):

        return None

    dataframe = daily_weather[
        required
    ].copy()

    dataframe[
        TARGET_VARIABLE
    ] = pd.to_numeric(
        dataframe[
            TARGET_VARIABLE
        ],
        errors="coerce",
    )

    dataframe = dataframe.dropna()

    groups = []

    for _, group in dataframe.groupby(
        "weather_condition"
    ):

        values = group[
            TARGET_VARIABLE
        ].to_numpy(
            dtype=float
        )

        if len(values) >= 2:
            groups.append(values)

    if len(groups) < 2:

        print(
            "Insufficient groups for ANOVA."
        )

        return None

    f_statistic, p_value = (
        stats.f_oneway(
            *groups
        )
    )

    total_n = sum(
        len(group)
        for group in groups
    )

    number_groups = len(groups)

    combined = np.concatenate(
        groups
    )

    grand_mean = float(
        combined.mean()
    )

    between_sum_squares = sum(
        len(group)
        * (
            float(group.mean())
            - grand_mean
        ) ** 2
        for group in groups
    )

    within_sum_squares = sum(
        np.sum(
            (
                group
                - float(group.mean())
            ) ** 2
        )
        for group in groups
    )

    total_sum_squares = (
        between_sum_squares
        + within_sum_squares
    )

    if total_sum_squares > 0:

        eta_squared = (
            between_sum_squares
            / total_sum_squares
        )

    else:

        eta_squared = np.nan

    print(
        f"Groups: {number_groups}"
    )

    print(
        f"Observations: {total_n}"
    )

    print(
        f"F-statistic: "
        f"{f_statistic:.4f}"
    )

    print(
        f"p-value: "
        f"{fmt_pvalue(p_value)}"
    )

    print(
        f"Eta-squared: "
        f"{eta_squared:.4f}"
    )

    print(
        f"Interpretation: "
        f"{significance_label(p_value)}"
    )

    print(
        "Important: ANOVA indicates whether at least "
        "one group differs; Tukey HSD is used next "
        "to identify pairwise differences."
    )

    result = {
        "groups": number_groups,
        "observations": total_n,
        "f_statistic": float(
            f_statistic
        ),
        "p_value": float(
            p_value
        ),
        "eta_squared": float(
            eta_squared
        ),
        "significance": significance_label(
            p_value
        ),
    }

    output_path = (
        OUTPUT_DIR
        / "weather_anova.csv"
    )

    pd.DataFrame(
        [result]
    ).to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved: {output_path}"
    )

    return result


# ============================================================================
# TUKEY HSD
# ============================================================================

def run_tukey_hsd(
    daily_weather: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "9. TUKEY HSD POST-HOC WEATHER COMPARISONS"
    )

    required = [
        "weather_condition",
        TARGET_VARIABLE,
    ]

    if not validate_dataset(
        "daily_weather",
        daily_weather,
        required,
    ):

        return pd.DataFrame()

    dataframe = daily_weather[
        required
    ].copy()

    dataframe[
        TARGET_VARIABLE
    ] = pd.to_numeric(
        dataframe[
            TARGET_VARIABLE
        ],
        errors="coerce",
    )

    dataframe = dataframe.dropna()

    if (
        dataframe[
            "weather_condition"
        ].nunique()
        < 2
    ):

        print(
            "Insufficient weather categories "
            "for Tukey HSD."
        )

        return pd.DataFrame()

    try:

        tukey = pairwise_tukeyhsd(
            endog=dataframe[
                TARGET_VARIABLE
            ],
            groups=dataframe[
                "weather_condition"
            ],
            alpha=ALPHA,
        )

    except Exception as exc:

        print(
            f"Tukey HSD failed: {exc}"
        )

        return pd.DataFrame()

    tukey_table = pd.DataFrame(
        data=tukey._results_table.data[1:],
        columns=tukey._results_table.data[0],
    )

    tukey_table = tukey_table.rename(
        columns={
            "group1": "group_1",
            "group2": "group_2",
            "meandiff": "mean_difference",
            "p-adj": "adjusted_p_value",
            "lower": "ci_lower",
            "upper": "ci_upper",
            "reject": "reject_null",
        }
    )

    print(
        tukey_table.to_string(
            index=False
        )
    )

    output_path = (
        OUTPUT_DIR
        / "tukey_weather_comparisons.csv"
    )

    tukey_table.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved: {output_path}"
    )

    return tukey_table


# ============================================================================
# REVENUE / WEATHER ANALYSIS
# ============================================================================

def calculate_revenue_weather_effects(
    revenue_weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze daily revenue by weather category.

    Revenue is compared using weather-category averages rather than
    comparing every individual day against a single arbitrary dry day.
    """

    print("\n" + "=" * 88)
    print("10. REVENUE → WEATHER ANALYSIS")
    print("=" * 88)

    validate_dataset(
        "revenue_weather",
        revenue_weather,
        [
            "trip_date",
            "gross_customer_charges_usd",
            "weather_condition",
        ],
    )

    dataframe = revenue_weather[
        [
            "trip_date",
            "gross_customer_charges_usd",
            "weather_condition",
        ]
    ].copy()

    dataframe["gross_customer_charges_usd"] = pd.to_numeric(
        dataframe["gross_customer_charges_usd"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=[
            "gross_customer_charges_usd",
            "weather_condition",
        ]
    )

    # ------------------------------------------------------------
    # REVENUE STATISTICS BY WEATHER CATEGORY
    # ------------------------------------------------------------

    revenue_summary = (
        dataframe
        .groupby("weather_condition")["gross_customer_charges_usd"]
        .agg(
            days="count",
            mean_revenue="mean",
            median_revenue="median",
            std_revenue="std",
            min_revenue="min",
            max_revenue="max",
        )
        .reset_index()
    )

    # ------------------------------------------------------------
    # DRY WEATHER BASELINE
    # ------------------------------------------------------------

    if "Dry" not in revenue_summary["weather_condition"].values:
        raise ValueError(
            "Dry weather category is required as the revenue baseline."
        )

    dry_revenue = revenue_summary.loc[
        revenue_summary["weather_condition"] == "Dry",
        "mean_revenue",
    ].iloc[0]

    revenue_summary["difference_vs_dry"] = (
        revenue_summary["mean_revenue"] - dry_revenue
    )

    revenue_summary["percent_change_vs_dry"] = (
        revenue_summary["difference_vs_dry"]
        / dry_revenue
        * 100
    )

    revenue_summary["baseline_category"] = "Dry"

    # ------------------------------------------------------------
    # DISPLAY RESULTS
    # ------------------------------------------------------------

    print(
        f"Average dry-day revenue baseline: "
        f"${dry_revenue:,.2f}"
    )

    print()

    print(
        revenue_summary[
            [
                "weather_condition",
                "days",
                "mean_revenue",
                "median_revenue",
                "std_revenue",
                "difference_vs_dry",
                "percent_change_vs_dry",
            ]
        ].to_string(index=False)
    )

    # ------------------------------------------------------------
    # SAVE OUTPUT
    # ------------------------------------------------------------

    output_path = (
        OUTPUT_DIR / "revenue_weather_effects.csv"
    )

    revenue_summary.to_csv(
        output_path,
        index=False,
    )

    print(f"\nSaved: {output_path}")

    return revenue_summary


def calculate_monthly_variability(
    monthly_trips: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "11. MONTHLY DEMAND VARIABILITY"
    )

    values = numeric_series(
        monthly_trips,
        TARGET_VARIABLE,
    ).dropna()

    if len(values) < 2:

        print(
            "Insufficient monthly observations."
        )

        return pd.DataFrame()

    mean = float(
        values.mean()
    )

    std = float(
        values.std(
            ddof=1
        )
    )

    minimum = float(
        values.min()
    )

    maximum = float(
        values.max()
    )

    cv = (
        std
        / mean
        * 100
        if mean != 0
        else np.nan
    )

    print(
        f"mean_monthly_trips: "
        f"{mean:,.2f}"
    )

    print(
        f"std_monthly_trips: "
        f"{std:,.2f}"
    )

    print(
        f"min_monthly_trips: "
        f"{minimum:,.2f}"
    )

    print(
        f"max_monthly_trips: "
        f"{maximum:,.2f}"
    )

    print(
        f"coefficient_of_variation_pct: "
        f"{cv:.2f}%"
    )

    result = pd.DataFrame(
        [
            {
                "mean_monthly_trips": mean,
                "std_monthly_trips": std,
                "min_monthly_trips": minimum,
                "max_monthly_trips": maximum,
                "coefficient_of_variation_pct": cv,
            }
        ]
    )

    result.to_csv(
        OUTPUT_DIR
        / "monthly_demand_variability.csv",
        index=False,
    )

    return result


# ============================================================================
# HOURLY DEMAND CONCENTRATION
# ============================================================================

def calculate_hourly_concentration(
    hourly_trips: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate concentration of hourly demand.

    IMPORTANT:
    The BigQuery loader returns:

        pickup_hour
        total_trips
        avg_trip_distance_miles

    Therefore this function intentionally uses total_trips.

    It does NOT expect an avg_trips column.
    """

    section(
        "12. HOURLY DEMAND CONCENTRATION"
    )

    if hourly_trips is None:

        print(
            "Hourly dataset unavailable."
        )

        return pd.DataFrame()

    if hourly_trips.empty:

        print(
            "Hourly dataset is empty."
        )

        return pd.DataFrame()

    required = [
        "pickup_hour",
        "total_trips",
    ]

    if not validate_dataset(
        "hourly",
        hourly_trips,
        required,
    ):

        return pd.DataFrame()

    dataframe = hourly_trips[
        required
    ].copy()

    dataframe[
        "pickup_hour"
    ] = pd.to_numeric(
        dataframe[
            "pickup_hour"
        ],
        errors="coerce",
    )

    dataframe[
        "total_trips"
    ] = pd.to_numeric(
        dataframe[
            "total_trips"
        ],
        errors="coerce",
    )

    dataframe = dataframe.dropna()

    if dataframe.empty:

        print(
            "No valid hourly observations."
        )

        return pd.DataFrame()

    # Aggregate again defensively in case the loader ever returns
    # more than one record for a given hour.
    hourly = (
        dataframe
        .groupby(
            "pickup_hour",
            as_index=False,
        )[
            "total_trips"
        ]
        .sum()
    )

    hourly = hourly.sort_values(
        "total_trips",
        ascending=False,
    )

    total = float(
        hourly[
            "total_trips"
        ].sum()
    )

    if total <= 0:

        print(
            "Hourly total demand is zero or invalid."
        )

        return pd.DataFrame()

    top_3 = float(
        hourly[
            "total_trips"
        ].head(3).sum()
    )

    top_5 = float(
        hourly[
            "total_trips"
        ].head(5).sum()
    )

    top_10 = float(
        hourly[
            "total_trips"
        ].head(10).sum()
    )

    top_3_share = (
        top_3
        / total
        * 100
    )

    top_5_share = (
        top_5
        / total
        * 100
    )

    top_10_share = (
        top_10
        / total
        * 100
    )

    peak_row = hourly.iloc[0]

    peak_hour = int(
        peak_row[
            "pickup_hour"
        ]
    )

    peak_hour_trips = float(
        peak_row[
            "total_trips"
        ]
    )

    result = pd.DataFrame(
        [
            {
                "hours_analyzed": int(
                    len(hourly)
                ),
                "total_trips": total,
                "peak_hour": peak_hour,
                "peak_hour_trips": peak_hour_trips,
                "top_3_hours_share_pct": top_3_share,
                "top_5_hours_share_pct": top_5_share,
                "top_10_hours_share_pct": top_10_share,
            }
        ]
    )

    print(
        f"Hours analyzed: "
        f"{len(hourly)}"
    )

    print(
        f"Total hourly trips: "
        f"{total:,.0f}"
    )

    print(
        f"Peak hour: "
        f"{peak_hour}"
    )

    print(
        f"Peak-hour trips: "
        f"{peak_hour_trips:,.0f}"
    )

    print(
        f"Top 3 hours share: "
        f"{top_3_share:.2f}%"
    )

    print(
        f"Top 5 hours share: "
        f"{top_5_share:.2f}%"
    )

    print(
        f"Top 10 hours share: "
        f"{top_10_share:.2f}%"
    )

    print()
    print(
        "Top hourly demand:"
    )

    print(
        hourly.head(10).to_string(
            index=False
        )
    )

    output_path = (
        OUTPUT_DIR
        / "hourly_demand_concentration.csv"
    )

    result.to_csv(
        output_path,
        index=False,
    )

    hourly.to_csv(
        OUTPUT_DIR
        / "hourly_demand_ranked.csv",
        index=False,
    )

    print()
    print(
        f"Saved: {output_path}"
    )

    print(
        f"Saved: "
        f"{OUTPUT_DIR / 'hourly_demand_ranked.csv'}"
    )

    return result


# ============================================================================
# WEEKDAY DEMAND VARIABILITY
# ============================================================================

def calculate_weekday_variability(
    weekday_trips: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "13. WEEKDAY DEMAND VARIABILITY"
    )

    if weekday_trips is None:

        print(
            "Weekday dataset unavailable."
        )

        return pd.DataFrame()

    if weekday_trips.empty:

        print(
            "Weekday dataset is empty."
        )

        return pd.DataFrame()

    if not validate_dataset(
        "weekday",
        weekday_trips,
        [TARGET_VARIABLE],
    ):

        return pd.DataFrame()

    values = numeric_series(
        weekday_trips,
        TARGET_VARIABLE,
    ).dropna()

    if len(values) < 2:

        print(
            "Insufficient weekday observations."
        )

        return pd.DataFrame()

    mean = float(
        values.mean()
    )

    std = float(
        values.std(
            ddof=1
        )
    )

    minimum = float(
        values.min()
    )

    maximum = float(
        values.max()
    )

    demand_range = (
        maximum
        - minimum
    )

    cv = (
        std
        / mean
        * 100
        if mean != 0
        else np.nan
    )

    print(
        f"mean: {mean:,.2f}"
    )

    print(
        f"std: {std:,.2f}"
    )

    print(
        f"min: {minimum:,.2f}"
    )

    print(
        f"max: {maximum:,.2f}"
    )

    print(
        f"range: {demand_range:,.2f}"
    )

    print(
        f"coefficient_of_variation_pct: "
        f"{cv:.2f}%"
    )

    result = pd.DataFrame(
        [
            {
                "mean_weekday_trips": mean,
                "std_weekday_trips": std,
                "min_weekday_trips": minimum,
                "max_weekday_trips": maximum,
                "range_weekday_trips": demand_range,
                "coefficient_of_variation_pct": cv,
            }
        ]
    )

    result.to_csv(
        OUTPUT_DIR
        / "weekday_demand_variability.csv",
        index=False,
    )

    return result


# ============================================================================
# SPATIAL DEMAND CONCENTRATION
# ============================================================================

def calculate_spatial_concentration(
    zones: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "14. SPATIAL DEMAND CONCENTRATION"
    )

    if zones is None or zones.empty:

        print(
            "Pickup-zone dataset unavailable."
        )

        return pd.DataFrame()

    if not validate_dataset(
        "zones",
        zones,
        [TARGET_VARIABLE],
    ):

        return pd.DataFrame()

    dataframe = zones.copy()

    dataframe[
        TARGET_VARIABLE
    ] = pd.to_numeric(
        dataframe[
            TARGET_VARIABLE
        ],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=[
            TARGET_VARIABLE
        ]
    )

    if dataframe.empty:

        return pd.DataFrame()

    dataframe = dataframe.sort_values(
        TARGET_VARIABLE,
        ascending=False,
    )

    total_trips = float(
        dataframe[
            TARGET_VARIABLE
        ].sum()
    )

    top_5_trips = float(
        dataframe[
            TARGET_VARIABLE
        ].head(5).sum()
    )

    top_10_trips = float(
        dataframe[
            TARGET_VARIABLE
        ].head(10).sum()
    )

    top_5_share = (
        top_5_trips
        / total_trips
        * 100
        if total_trips != 0
        else np.nan
    )

    top_10_share = (
        top_10_trips
        / total_trips
        * 100
        if total_trips != 0
        else np.nan
    )

    median_trips = float(
        dataframe[
            TARGET_VARIABLE
        ].median()
    )

    result = pd.DataFrame(
        [
            {
                "pickup_zones_analyzed": int(
                    len(dataframe)
                ),
                "total_trips": total_trips,
                "top_5_zone_share_pct": top_5_share,
                "top_10_zone_share_pct": top_10_share,
                "median_zone_trips": median_trips,
            }
        ]
    )

    print(
        f"Pickup zones analyzed: "
        f"{len(dataframe)}"
    )

    print(
        f"Top 5 zone share: "
        f"{top_5_share:.2f}%"
    )

    print(
        f"Top 10 zone share: "
        f"{top_10_share:.2f}%"
    )

    print(
        f"Median zone trips: "
        f"{median_trips:,.0f}"
    )

    result.to_csv(
        OUTPUT_DIR
        / "spatial_demand_concentration.csv",
        index=False,
    )

    dataframe.to_csv(
        OUTPUT_DIR
        / "pickup_zone_demand_ranked.csv",
        index=False,
    )

    return result


# ============================================================================
# INDIVIDUAL WEATHER VARIABLE REPORTS
# ============================================================================

def print_individual_weather_analysis(
    correlations: pd.DataFrame,
    regressions: pd.DataFrame,
) -> None:

    section(
        "15. INDIVIDUAL WEATHER VARIABLE ANALYSIS"
    )

    if correlations.empty:

        print(
            "Weather correlation results unavailable."
        )

        return

    for _, row in correlations.iterrows():

        variable = row[
            "variable"
        ]

        print()
        print(
            f"{variable} → {TARGET_VARIABLE}"
        )

        print(
            f"  n = {int(row['n'])}"
        )

        print(
            f"  Pearson r = "
            f"{row['pearson_r']:.4f}"
        )

        print(
            f"  Pearson strength = "
            f"{row['pearson_strength']}"
        )

        print(
            f"  Pearson p-value = "
            f"{fmt_pvalue(row['pearson_p_value'])}"
        )

        print(
            f"  Pearson result = "
            f"{row['pearson_significance']}"
        )

        print(
            f"  Spearman rho = "
            f"{row['spearman_rho']:.4f}"
        )

        print(
            f"  Spearman p-value = "
            f"{fmt_pvalue(row['spearman_p_value'])}"
        )

        if not regressions.empty:

            matches = regressions[
                regressions[
                    "x"
                ].eq(variable)
            ]

            if not matches.empty:

                regression = matches.iloc[0]

                print()
                print(
                    f"  Coefficient = "
                    f"{regression['coefficient']:.4f}"
                )

                print(
                    f"  R² = "
                    f"{regression['r_squared']:.4f}"
                )

                print(
                    f"  Coefficient p-value = "
                    f"{fmt_pvalue(regression['coefficient_p_value'])}"
                )

                print(
                    "  95% coefficient CI = "
                    f"["
                    f"{regression['coefficient_ci_lower']:.4f}, "
                    f"{regression['coefficient_ci_upper']:.4f}"
                    f"]"
                )


# ============================================================================
# DAILY DEMAND CONFIDENCE INTERVAL
# ============================================================================

def calculate_daily_demand_confidence_interval(
    daily_weather: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "19. 95% CONFIDENCE INTERVAL"
    )

    values = numeric_series(
        daily_weather,
        TARGET_VARIABLE,
    ).dropna()

    if len(values) < 2:

        print(
            "Insufficient daily observations."
        )

        return pd.DataFrame()

    n = len(values)

    mean = float(
        values.mean()
    )

    std = float(
        values.std(
            ddof=1
        )
    )

    standard_error = (
        std
        / np.sqrt(n)
    )

    critical_value = float(
        stats.t.ppf(
            1 - ALPHA / 2,
            df=n - 1,
        )
    )

    margin_of_error = (
        critical_value
        * standard_error
    )

    lower_bound = (
        mean
        - margin_of_error
    )

    upper_bound = (
        mean
        + margin_of_error
    )

    print(
        f"Observation count: {n}"
    )

    print(
        f"Mean daily trips: "
        f"{mean:,.2f}"
    )

    print(
        f"95% CI lower bound: "
        f"{lower_bound:,.2f}"
    )

    print(
        f"95% CI upper bound: "
        f"{upper_bound:,.2f}"
    )

    result = pd.DataFrame(
        [
            {
                "observations": n,
                "mean_daily_trips": mean,
                "standard_deviation": std,
                "standard_error": standard_error,
                "confidence_level": 0.95,
                "critical_value": critical_value,
                "margin_of_error": margin_of_error,
                "ci_lower": lower_bound,
                "ci_upper": upper_bound,
            }
        ]
    )

    result.to_csv(
        OUTPUT_DIR
        / "daily_demand_confidence_interval.csv",
        index=False,
    )

    return result


# ============================================================================
# STATISTICAL FINDINGS SUMMARY
# ============================================================================

def build_statistical_findings_summary(
    correlations: pd.DataFrame,
    anova_result: dict[str, float] | None,
    multivariate_model: pd.DataFrame,
) -> pd.DataFrame:

    section(
        "20. STATISTICAL FINDINGS SUMMARY"
    )

    findings = []

    if not correlations.empty:

        for _, row in correlations.iterrows():

            findings.append(
                {
                    "finding_type": "correlation",
                    "variable": row[
                        "variable"
                    ],
                    "target": row[
                        "target"
                    ],
                    "pearson_r": row[
                        "pearson_r"
                    ],
                    "pearson_p_value": row[
                        "pearson_p_value"
                    ],
                    "spearman_rho": row[
                        "spearman_rho"
                    ],
                    "spearman_p_value": row[
                        "spearman_p_value"
                    ],
                    "interpretation": (
                        f"{row['pearson_strength']} "
                        f"{'positive' if row['pearson_r'] > 0 else 'negative'} "
                        "relationship"
                    ),
                    "statistically_significant": (
                        row[
                            "pearson_p_value"
                        ]
                        < ALPHA
                    ),
                }
            )

    if anova_result is not None:

        findings.append(
            {
                "finding_type": "anova",
                "variable": "weather_condition",
                "target": TARGET_VARIABLE,
                "pearson_r": np.nan,
                "pearson_p_value": np.nan,
                "spearman_rho": np.nan,
                "spearman_p_value": np.nan,
                "interpretation": (
                    "Weather categories show statistically "
                    "significant differences in daily demand"
                ),
                "statistically_significant": (
                    anova_result[
                        "p_value"
                    ]
                    < ALPHA
                ),
            }
        )

    if not multivariate_model.empty:

        row = multivariate_model.iloc[0]

        findings.append(
            {
                "finding_type": "multivariate_regression",
                "variable": "weather_variables",
                "target": TARGET_VARIABLE,
                "pearson_r": np.nan,
                "pearson_p_value": np.nan,
                "spearman_rho": np.nan,
                "spearman_p_value": np.nan,
                "interpretation": (
                    "Multivariate weather model is "
                    f"{row['model_significance']} "
                    f"with R²={row['r_squared']:.4f}"
                ),
                "statistically_significant": (
                    row[
                        "model_p_value"
                    ]
                    < ALPHA
                ),
            }
        )

    result = pd.DataFrame(
        findings
    )

    print(
        result.to_string(
            index=False
        )
    )

    output_path = (
        OUTPUT_DIR
        / "statistical_findings_summary.csv"
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved: {output_path}"
    )

    return result


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """Run the complete statistical analysis pipeline."""

    print()
    print(
        "URBAN MOBILITY ANALYTICS"
    )

    print(
        "STATISTICAL ANALYSIS ENGINE"
    )

    print()
    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    # ========================================================================
    # 1. LOAD DATA
    # ========================================================================

    section(
        "1. LOADING ANALYTICAL DATA"
    )

    print(
        "Loading monthly demand..."
    )

    monthly_trips = (
        load_monthly_trips()
    )

    print(
        f"Monthly dataset: "
        f"{monthly_trips.shape}"
    )

    print(
        "Loading hourly demand..."
    )

    hourly_trips = (
        load_hourly_trips()
    )

    print(
        f"Hourly dataset: "
        f"{hourly_trips.shape}"
    )

    print(
        "Loading weekday demand..."
    )

    weekday_trips = (
        load_weekday_trips()
    )

    print(
        f"Weekday dataset: "
        f"{weekday_trips.shape}"
    )

    print(
        "Loading pickup-zone demand..."
    )

    zones = (
        load_pickup_zones()
    )

    print(
        f"Zones dataset: "
        f"{zones.shape}"
    )

    print(
        "Loading daily weather..."
    )

    daily_weather = (
        load_daily_weather()
    )

    print(
        f"Daily Weather dataset: "
        f"{daily_weather.shape}"
    )

    print(
        "Loading weather impact..."
    )

    weather_impact = (
        load_weather_impact()
    )

    print(
        f"Weather Impact dataset: "
        f"{weather_impact.shape}"
    )

    print(
        "Loading temperature impact..."
    )

    temperature_impact = (
        load_temperature_impact()
    )

    print(
        f"Temperature dataset: "
        f"{temperature_impact.shape}"
    )

    print(
        "Loading precipitation impact..."
    )

    precipitation_impact = (
        load_precipitation_impact()
    )

    print(
        f"Precipitation dataset: "
        f"{precipitation_impact.shape}"
    )

    print(
        "Loading snowfall impact..."
    )

    snowfall_impact = (
        load_snowfall_impact()
    )

    print(
        f"Snowfall dataset: "
        f"{snowfall_impact.shape}"
    )

    print(
        "Loading wind impact..."
    )

    wind_impact = (
        load_wind_impact()
    )

    print(
        f"Wind dataset: "
        f"{wind_impact.shape}"
    )

    print(
        "Loading weekday/weather interaction..."
    )

    weekday_weather = (
        load_weekday_weather_impact()
    )

    print(
        f"Weekday Weather dataset: "
        f"{weekday_weather.shape}"
    )

    print(
        "Loading revenue/weather relationship..."
    )

    revenue_weather = (
        load_revenue_weather_daily()
    )

    print(
        f"Revenue Weather dataset: "
        f"{revenue_weather.shape}"
    )

    # ========================================================================
    # 2. VALIDATION
    # ========================================================================

    validate_all_datasets(
        monthly_trips,
        hourly_trips,
        weekday_trips,
        zones,
        daily_weather,
        weather_impact,
        revenue_weather,
    )

    # ========================================================================
    # 3. CORRELATION
    # ========================================================================

    correlations = (
        calculate_weather_correlations(
            daily_weather
        )
    )

    # ========================================================================
    # 4. SIMPLE REGRESSIONS
    # ========================================================================

    regressions = (
        calculate_weather_regressions(
            daily_weather
        )
    )

    # ========================================================================
    # 5. MULTIVARIATE REGRESSION
    # ========================================================================

    (
        multivariate_coefficients,
        multivariate_model,
        multivariate_diagnostics,
    ) = run_multivariate_weather_regression(
        daily_weather
    )

    # ========================================================================
    # 6. VIF
    # ========================================================================

    calculate_vif(
        daily_weather
    )

    # ========================================================================
    # 7. WEATHER EFFECT SIZES
    # ========================================================================

    calculate_weather_effect_sizes(
        daily_weather
    )

    # ========================================================================
    # 8. ANOVA
    # ========================================================================

    anova_result = (
        run_weather_anova(
            daily_weather
        )
    )

    # ========================================================================
    # 9. TUKEY
    # ========================================================================

    run_tukey_hsd(
        daily_weather
    )

    # ========================================================================
    # 10. REVENUE / WEATHER
    # ========================================================================

    calculate_revenue_weather_effects(
        revenue_weather
    )

    # ========================================================================
    # 11. MONTHLY
    # ========================================================================

    calculate_monthly_variability(
        monthly_trips
    )

    # ========================================================================
    # 12. HOURLY
    # ========================================================================

    calculate_hourly_concentration(
        hourly_trips
    )

    # ========================================================================
    # 13. WEEKDAY
    # ========================================================================

    calculate_weekday_variability(
        weekday_trips
    )

    # ========================================================================
    # 14. SPATIAL
    # ========================================================================

    calculate_spatial_concentration(
        zones
    )

    # ========================================================================
    # 15. INDIVIDUAL WEATHER REPORT
    # ========================================================================

    print_individual_weather_analysis(
        correlations,
        regressions,
    )

    # ========================================================================
    # 19. CONFIDENCE INTERVAL
    # ========================================================================

    calculate_daily_demand_confidence_interval(
        daily_weather
    )

    # ========================================================================
    # 20. FINDINGS SUMMARY
    # ========================================================================

    build_statistical_findings_summary(
        correlations,
        anova_result,
        multivariate_model,
    )

    # ========================================================================
    # COMPLETE
    # ========================================================================

    section(
        "21. ANALYSIS COMPLETE"
    )

    print(
        "Statistical analysis completed successfully."
    )

    print()
    print(
        "Output files written to:"
    )

    print(
        OUTPUT_DIR
    )

    print()
    print(
        "Generated analytical outputs:"
    )

    generated_files = sorted(
        OUTPUT_DIR.glob(
            "*.csv"
        )
    )

    for file_path in generated_files:

        print(
            f"  - {file_path.name}"
        )

    print()
    print(
        "Interpretation note:"
    )

    print(
        "Correlation and regression identify statistical "
        "associations in the available historical data. "
        "They do not, by themselves, establish causation."
    )

    print()
    print(
        "The multivariate model estimates the relationship "
        "between daily taxi demand and weather variables "
        "while considering the weather predictors jointly."
    )

    print()
    print(
        "ANOVA determines whether weather-category means "
        "differ overall. Tukey HSD identifies which pairs "
        "of weather categories differ after the overall "
        "ANOVA test."
    )

    print()
    print(
        "Statistical significance should always be "
        "interpreted alongside effect size, model fit, "
        "data quality, and operational relevance."
    )

    print()


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()