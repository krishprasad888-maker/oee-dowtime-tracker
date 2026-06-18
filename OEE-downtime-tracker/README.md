# OEE Downtime Tracker

A Python tool for calculating, visualising, and reporting **Overall Equipment Effectiveness (OEE)** across manufacturing production lines.

Built as a practical demonstration of data-driven continuous improvement — the same methodology used in Lean Six Sigma and DMAIC-based process improvement programs.

---

## What is OEE?

OEE measures how effectively a manufacturing operation is running compared to its full potential.

```
OEE = Availability × Performance × Quality
```

| Factor | Formula | What it measures |
|---|---|---|
| **Availability** | (Planned Time − Downtime) / Planned Time | Machine uptime vs schedule |
| **Performance** | (Ideal Cycle Time × Units Produced) / Run Time | Speed vs ideal rate |
| **Quality** | Good Units / Total Units Produced | First-pass yield rate |

**World-class benchmark: OEE ≥ 85%**

---

## Features

- Calculates OEE (Availability × Performance × Quality) per shift, per line, and per day
- Generates a **Pareto chart** of downtime reasons to identify the vital few causes (80/20 rule)
- Plots **OEE trend over time** with world-class benchmark line
- Produces an **OEE component breakdown** (A, P, Q) per production line
- Outputs an **availability heatmap** (line × date) for quick visual scanning
- Exports a colour-coded **Excel report** (green ≥ 85%, amber ≥ 70%, red < 70%)
- Works with any CSV downtime log — not tied to a specific machine or facility

---

## Charts produced

| Chart | What it shows |
|---|---|
| `1_oee_trend.png` | Daily OEE vs world-class benchmark, gap highlighted |
| `2_pareto_downtime.png` | Downtime minutes by reason with cumulative % line |
| `3_component_breakdown.png` | A, P, Q scores by line with OEE overlay |
| `4_availability_heatmap.png` | Colour-coded availability grid (line × date) |

---

## Project structure

```
oee_tracker/
├── data/
│   └── downtime_log.csv       # Input: shift-level downtime log
├── charts/                    # Output: PNG charts
├── outputs/                   # Output: Excel report
├── oee_calculator.py          # Core OEE calculation engine
├── charts.py                  # Chart generation (matplotlib)
├── report_generator.py        # Excel report (openpyxl)
├── main.py                    # Entry point
├── requirements.txt
└── README.md
```

---

## Quick start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/oee-downtime-tracker.git
cd oee-downtime-tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run with sample data
python main.py

# 4. Run with your own data
python main.py --data your_data.csv --report MyReport.xlsx
```

---

## Input data format

Your CSV must include these columns:

| Column | Description | Example |
|---|---|---|
| `date` | Shift date | 2024-01-08 |
| `shift` | Day / Night | Day |
| `line` | Production line name | Conveyor_A |
| `planned_production_time_min` | Total planned minutes | 480 |
| `downtime_min` | Actual downtime minutes | 35 |
| `ideal_cycle_time_sec` | Target cycle time (seconds/unit) | 3.0 |
| `total_units_produced` | All units produced | 8400 |
| `good_units` | Units passing quality check | 8100 |
| `downtime_reason` | Reason category | Mechanical failure |

---

## Sample output (console)

```
📊 OEE by Production Line
Conveyor_A       OEE: 85.1%  A:93.2%  P:93.1%  Q:97.9%  ✅
Packaging_C      OEE: 92.8%  A:95.3%  P:98.7%  Q:98.5%  ✅
Rounder_B        OEE: 86.3%  A:91.6%  P:96.8%  Q:97.4%  ✅

🔧 Top Downtime Reasons (Pareto)
Mechanical failure       392 min  (41.1%)  cumulative: 41.1%
Unplanned breakdown      340 min  (35.7%)  cumulative: 76.8%
Changeover               147 min  (15.4%)  cumulative: 92.2%
Planned maintenance       74 min   (7.8%)  cumulative: 100.0%
```

---

## Requirements

```
pandas>=2.0
matplotlib>=3.7
openpyxl>=3.1
```

---

## Background

This project was built to demonstrate practical application of Lean Six Sigma and continuous improvement principles using Python. The OEE formula, Pareto analysis, and DMAIC-based root cause framing are standard tools in process quality engineering.

The sample dataset is modelled on a food manufacturing environment with three production lines (conveyor, rounder, packaging) — common in bakery and food processing operations.

---

## Author

**Krishnaprasad Shanmugam**
M.Sc. Mechanical Engineering | Lean Six Sigma Green Belt | Process Quality Engineering
[LinkedIn](https://linkedin.com/in/krishna-prasad-022)
