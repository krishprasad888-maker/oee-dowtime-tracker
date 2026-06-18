"""
main.py
-------
OEE Downtime Tracker — main runner.

Usage:
    python main.py
    python main.py --data data/downtime_log.csv
    python main.py --data your_file.csv --report MyReport.xlsx

Output:
    charts/   — 4 PNG charts
    outputs/  — Excel report
"""

import argparse
import sys
from oee_calculator import load_data, calculate_oee, summarise_by_line, summarise_by_date, downtime_pareto
from charts import plot_oee_trend, plot_pareto, plot_component_breakdown, plot_availability_heatmap
from report_generator import generate_report


def print_console_summary(df_by_line, df_by_date, pareto):
    print("\n" + "=" * 55)
    print("  OEE DOWNTIME TRACKER — RESULTS SUMMARY")
    print("=" * 55)

    print("\n📊 OEE by Production Line")
    print("-" * 55)
    for _, row in df_by_line.iterrows():
        oee_flag = "✅" if row["avg_oee"] >= 85 else ("⚠️ " if row["avg_oee"] >= 70 else "❌")
        print(f"  {row['line']:<16} OEE: {row['avg_oee']:>5.1f}%  "
              f"A:{row['avg_availability']:.1f}%  "
              f"P:{row['avg_performance']:.1f}%  "
              f"Q:{row['avg_quality']:.1f}%  {oee_flag}")

    print(f"\n📅 OEE by Date (all lines averaged)")
    print("-" * 55)
    for _, row in df_by_date.iterrows():
        bar_len = int(row["avg_oee"] / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  {row['date'].strftime('%d %b')}  [{bar}] {row['avg_oee']:.1f}%")

    print(f"\n🔧 Top Downtime Reasons (Pareto)")
    print("-" * 55)
    total = pareto.sum()
    cumulative = 0
    for reason, minutes in pareto.items():
        pct = minutes / total * 100
        cumulative += pct
        print(f"  {reason:<28} {minutes:>5} min  ({pct:.1f}%)  cumulative: {cumulative:.1f}%")

    print("\n" + "=" * 55)
    print("  World-class OEE benchmark: 85%")
    print("  Green ✅ >= 85%   |   Amber ⚠️  >= 70%   |   Red ❌ < 70%")
    print("=" * 55 + "\n")


def main():
    parser = argparse.ArgumentParser(description="OEE Downtime Tracker")
    parser.add_argument("--data",   default="data/downtime_log.csv", help="Path to CSV data file")
    parser.add_argument("--report", default="OEE_Report.xlsx",       help="Output Excel filename")
    args = parser.parse_args()

    print(f"\nLoading data from: {args.data}")
    df = load_data(args.data)
    df = calculate_oee(df)

    df_by_line = summarise_by_line(df)
    df_by_date = summarise_by_date(df)
    pareto     = downtime_pareto(df)

    print_console_summary(df_by_line, df_by_date, pareto)

    print("Generating charts...")
    plot_oee_trend(df_by_date)
    plot_pareto(pareto)
    plot_component_breakdown(df_by_line)
    plot_availability_heatmap(df)

    print("\nGenerating Excel report...")
    report_path = generate_report(df, df_by_line, pareto, filename=args.report)

    print(f"\n✅ All done.")
    print(f"   Charts  → charts/")
    print(f"   Report  → {report_path}\n")


if __name__ == "__main__":
    main()
