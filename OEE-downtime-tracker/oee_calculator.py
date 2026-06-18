"""
oee_calculator.py
-----------------
Core OEE calculation engine.

OEE = Availability x Performance x Quality

Availability  = (Planned Time - Downtime) / Planned Time
Performance   = (Ideal Cycle Time x Units Produced) / Run Time
Quality       = Good Units / Total Units Produced

World-class OEE benchmark: >= 85%
"""

import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """Load and validate downtime log CSV."""
    df = pd.read_csv(filepath, parse_dates=["date"])
    required_cols = [
        "date", "shift", "line",
        "planned_production_time_min", "downtime_min",
        "ideal_cycle_time_sec", "total_units_produced",
        "good_units", "downtime_reason"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in data: {missing}")
    return df


def calculate_oee(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Availability, Performance, Quality, and OEE columns to dataframe.
    All values expressed as percentages (0-100).
    """
    df = df.copy()

    # Run time = planned time minus downtime (minutes)
    df["run_time_min"] = df["planned_production_time_min"] - df["downtime_min"]

    # Availability: how much of planned time the machine was actually running
    df["availability"] = (
        df["run_time_min"] / df["planned_production_time_min"]
    ) * 100

    # Performance: how fast vs ideal speed during run time
    # ideal_cycle_time in seconds -> convert run time to seconds
    df["run_time_sec"] = df["run_time_min"] * 60
    df["performance"] = (
        (df["ideal_cycle_time_sec"] * df["total_units_produced"])
        / df["run_time_sec"]
    ) * 100
    # Cap at 100% (occasional over-speed is recorded but capped)
    df["performance"] = df["performance"].clip(upper=100)

    # Quality: ratio of good output to total output
    df["quality"] = (df["good_units"] / df["total_units_produced"]) * 100

    # OEE: product of all three factors
    df["oee"] = (
        (df["availability"] / 100)
        * (df["performance"] / 100)
        * (df["quality"] / 100)
    ) * 100

    return df


def summarise_by_line(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate OEE metrics by production line."""
    return (
        df.groupby("line")
        .agg(
            avg_availability=("availability", "mean"),
            avg_performance=("performance", "mean"),
            avg_quality=("quality", "mean"),
            avg_oee=("oee", "mean"),
            total_downtime_min=("downtime_min", "sum"),
            shifts_recorded=("oee", "count"),
        )
        .round(2)
        .reset_index()
    )


def summarise_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate OEE metrics by date (all lines combined)."""
    return (
        df.groupby("date")
        .agg(
            avg_oee=("oee", "mean"),
            avg_availability=("availability", "mean"),
            avg_performance=("performance", "mean"),
            avg_quality=("quality", "mean"),
            total_downtime_min=("downtime_min", "sum"),
        )
        .round(2)
        .reset_index()
    )


def downtime_pareto(df: pd.DataFrame) -> pd.Series:
    """Return total downtime minutes grouped by reason, sorted descending."""
    return (
        df.groupby("downtime_reason")["downtime_min"]
        .sum()
        .sort_values(ascending=False)
    )


if __name__ == "__main__":
    df = load_data("data/downtime_log.csv")
    df = calculate_oee(df)

    print("\n=== OEE by Line ===")
    print(summarise_by_line(df).to_string(index=False))

    print("\n=== OEE by Date ===")
    print(summarise_by_date(df).to_string(index=False))

    print("\n=== Downtime Pareto ===")
    print(downtime_pareto(df))
