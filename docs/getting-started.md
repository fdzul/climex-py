# Getting Started

## Points

`download_nasa_power_data()` takes a table with one row per point and the
columns `latitude` and `longitude` (decimal degrees, WGS84). With
[rgeomex](https://fdzul.github.io/rgeomex-py/) the points can be the
centroids of the municipalities of a state:

```python
import rgeomex
import climex

mun = rgeomex.load("AGEM_inegi19_mx", cve_edo="31")          # Yucatán
pts = climex.centroids(mun, id_col="CVEGEO")                  # a point inside each one

clima = climex.download_nasa_power_data(
    pts, id_col="CVEGEO",
    parameters=["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M"],
    start_date="20240101", end_date="20241231", community="AG")
```

Each point is saved as `<identifier>.csv` in `output_folder`
(`./nasa_power_data` by default), and the result joins all of them.
`centroids()` uses the representative point of each polygon, which is always
inside it (the centroid of a curved municipality can fall outside).

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
answers of the API are retried three times.

If the download stops (connection, many points), run the same call again:
the points whose CSV is already in `output_folder` are skipped
(`overwrite=True` downloads them again). The failed points are listed at the
end, and with `return_consolidated=False` the function returns the result
of each download (`success`, `error`).
