# Getting Started

## Municipalities

The package brings one point for each of the 2,465 municipalities of Mexico
(INEGI 2019), so the climate of a state or of all the country needs no other
data:

```python
import climex

yuc = climex.municipalities("31")              # the 106 municipalities of Yucatán
mx = climex.municipalities()                   # the 2,465 of the country
jal_yuc = climex.municipalities(["14", "31"])  # several states

clima = climex.download_nasa_power_data(
    yuc, id_col="CVEGEO",
    parameters=["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M"],
    start_date="20240101", end_date="20241231", community="AG")
```

The table has the keys (`CVEGEO`, `CVE_ENT`, `CVE_MUN`), the names of the
state and the municipality, the point (`latitude`, `longitude`) and the area.
By default the point is always inside the municipality (its representative
point); `point="centroid"` uses the geometric centroid, which falls outside
67 curved or fragmented municipalities (column `centroid_inside`).

Each point is saved as `<identifier>.csv` in `output_folder`
(`./nasa_power_data` by default), and the result joins all of them.

## Other points

`download_nasa_power_data()` takes any table with one row per point and the
columns `latitude` and `longitude` (decimal degrees, WGS84). For polygons,
e.g. the AGEB or localities of [rgeomex](https://fdzul.github.io/rgeomex-py/),
`centroids()` gives a point inside each one:

```python
import rgeomex

ageb = rgeomex.extract_ageb(locality="Merida", cve_edo="31")["ageb"]
pts = climex.centroids(ageb, id_col="CVEGEO")
clima = climex.download_nasa_power_data(pts, id_col="CVEGEO", parameters=["T2M"],
                                        start_date="20240101", end_date="20241231")
```

## Temporal resolution

| `temporal_resolution` | Rows | Period |
|---|---|---|
| `"daily"` | one per day (`date`) | `start_date` to `end_date` (`"YYYYMMDD"`) |
| `"monthly"` | one per year and month (`year`, `month`) | the years of `start_date` and `end_date` |
| `"climatology"` | one per month and the annual mean (`period`) | long-term average |

## Parameters

| Group | Parameters |
|---|---|
| Temperature (°C) | `T2M`, `T2M_MAX`, `T2M_MIN`, `T2M_RANGE`, `T2MDEW`, `T2MWET`, `TS` |
| Precipitation (mm/day) | `PRECTOTCORR` |
| Humidity | `RH2M` (%), `QV2M` (g/kg) |
| Wind (m/s) | `WS2M`, `WS10M`, `WD2M`, `WD10M` |
| Radiation | `ALLSKY_SFC_SW_DWN`, `CLRSKY_SFC_SW_DWN`, `ALLSKY_SFC_LW_DWN` |
| Pressure (kPa) | `PS` |

The full list is in the
[NASA POWER parameter dictionary](https://power.larc.nasa.gov/parameters/).
`community` (`"RE"`, `"AG"` or `"SB"`) changes only the units of some
parameters; `"AG"` (agroclimatology) gives precipitation in mm/day.

## Requests

NASA asks for at most 5 simultaneous requests, so `processes` is limited to
5; with `processes=1` the points are downloaded one after the other. Busy
answers of the API are retried three times, and the points that still fail
get a second round at the end.

The result has only the period requested, with one row per point and date
(no duplicates), sorted by point and date. At the end the function reports
whether every point has all the period and how many rows have no data
(NaN): usually the last days, not yet published by NASA POWER.

If the download stops (connection, many points), run the same call again:
the points whose CSV in `output_folder` already has the period, with data in
every day, are skipped; the rest are downloaded again (the CSV is replaced,
never appended, so nothing is duplicated).
For an update (the same folder with a later `end_date`) the points are
downloaded again; `overwrite=True` downloads everything again. The failed points are listed at the
end, and with `return_consolidated=False` the function returns the result
of each download (`success`, `error`).
