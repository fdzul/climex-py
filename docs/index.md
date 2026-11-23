# climex documentation <img src="assets/logo.png" align="right" width="130" style="width:130px" alt="" />

## Welcome

The **climex** package downloads climate data of Mexico from the
[NASA POWER](https://power.larc.nasa.gov) API: daily, monthly or
climatological temperature, precipitation, humidity, wind and radiation for
the **2,465 municipalities of Mexico** (INEGI 2019), whose points come with
the package, or for any set of points, such as the AGEB or localities of a
city. It downloads one request per point with all the period, up to five at
a time, retries when the API is busy, can be stopped and resumed, and
returns one row per point and date, without duplicates.

## Philosophy

The authors' vision is to create data packages, functions, or a combination
of both in **Julia**, **R**, and **Python**, contributing to the
interoperability of algorithms and data to transform the information into
decisions that help solve specific problems.

In the case of **climex**, the climate is one of the main drivers of the
transmission of dengue and other vector-borne diseases: the package gives
the climatic covariates (temperature, humidity, precipitation) at the level
used by surveillance and early warning systems, the municipality, in a
single call. It is part of the [dengueverse](https://fdzul.github.io/dengueverse/),
and its R version is [climex](https://github.com/fdzul/climex).

## Getting Started

### Installation

#### From GitHub

```bash
pip install git+https://github.com/fdzul/climex-py
```

The package is installed as `climex-py` and imported as `climex`.

### Quick Start Tutorial

#### 1. Import the package

```python
import climex
```

#### 2. Choose the points

The municipalities of a state, of several states or of all the country:

```python
yuc = climex.municipalities("31")              # the 106 municipalities of Yucatán
mx = climex.municipalities()                   # the 2,465 of the country
```

#### 3. Download the climate

```python
clima = climex.download_nasa_power_data(
    yuc, id_col="CVEGEO",
    parameters=["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M"],
    start_date="20240101", end_date="20241231",
    temporal_resolution="daily", community="AG")
```

```text
106 points; parameters: T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M; daily; community AG; 5 processes
106/106 points downloaded in … s
38,796 rows; 106 points; no duplicates
complete: 106/106 points with all the period
```

#### 4. Use the data

```python
clima[["identifier", "date", "T2M"]].head(3)
#   identifier       date    T2M
# 0      31001 2024-01-01  21.98
# 1      31001 2024-01-02  22.32
# 2      31001 2024-01-03  23.03
```

See the [Quick Start](quickstart.md) for the details and the
[Examples](examples.md) for monthly data, the whole country, weekly updates
and the AGEB of a city.
