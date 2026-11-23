# Getting Started

This guide will help you install climex and download the climate of the
municipalities of a state in a few minutes.

## Prerequisites

Python 3.10 or higher. pandas and requests are installed automatically.

## Installation

```bash
pip install git+https://github.com/fdzul/climex-py
```

## 1. Your first download

```python
import climex

ags = climex.municipalities("01")            # the 11 municipalities of Aguascalientes
clima = climex.download_nasa_power_data(
    ags, id_col="CVEGEO",
    parameters=["T2M", "RH2M", "PRECTOTCORR"],
    start_date="20250101", end_date="20251231",
    community="AG", output_folder="nasa_power_ags")
```

## 2. What you get

- One row per municipality and day: `identifier` (the `CVEGEO`, with its
  leading zero), `latitude`, `longitude`, `date` and one column per
  parameter.
- Only the period requested, without duplicates, sorted by municipality and
  date.
- One CSV per municipality in `output_folder` (`01001.csv`, …).
- A report at the end: rows, points, whether every point has all the period,
  and the days without data.

## 3. Temporal resolution

| `temporal_resolution` | Rows | Period |
|---|---|---|
| `"daily"` | one per day (`date`) | `start_date` to `end_date` (`"YYYYMMDD"`) |
| `"monthly"` | one per year and month (`year`, `month`) | the years of `start_date` and `end_date` |
| `"climatology"` | one per month and the annual mean (`period`) | long-term average |

## 4. Stop, resume and update

!!! tip "Run it again"
    If the download stops (connection, many points), run the same call
    again: the points whose CSV in `output_folder` already has the period,
    with data in every day, are skipped. With a later `end_date` (a weekly
    update) the points are downloaded again; the CSV are replaced, never
    appended, so nothing is duplicated.

!!! note "Days not yet published"
    NASA POWER publishes the last days with a delay of a few days. Those
    days come as NaN and are asked again in the next run.

## 5. Requests

NASA asks for at most 5 simultaneous requests, so `processes` is limited to
5. Busy answers of the API (429, 5xx) are retried three times, and the points
that still fail get a second round at the end. A request can have up to 20
parameters.
