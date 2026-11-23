# Municipalities and parameters

## Municipalities

`climex.municipalities()` returns one point for each of the 2,465
municipalities of Mexico (INEGI 2019, Marco Geoestadístico), bundled with the
package:

| Column | Description |
|---|---|
| `CVEGEO` | Municipality key (5 digits: state + municipality) |
| `CVE_ENT`, `state` | State key and name |
| `CVE_MUN`, `municipality` | Municipality key and name |
| `latitude`, `longitude` | Point used to download (WGS84) |
| `centroid_lat`, `centroid_lon` | Geometric centroid |
| `centroid_inside` | Whether the centroid falls inside the municipality |
| `area_km2` | Area of the municipality |

```python
climex.municipalities("31")                  # one state
climex.municipalities(["14", "31"])          # several states
climex.municipalities()                      # all the country
climex.municipalities("31", point="centroid")
```

By default `latitude` and `longitude` are a point that is always inside the
municipality (its representative point). The geometric centroid falls outside
67 curved or fragmented municipalities, where NASA POWER would give the
climate of a neighbour or of the sea; `point="centroid"` uses it anyway.

The table is built with `data-raw/municipalities.py` from the polygons of
[rgeomex](https://fdzul.github.io/rgeomex-py/).

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

## Source

NASA POWER (Prediction Of Worldwide Energy Resources) gives daily data from
1981 for meteorology (MERRA-2 reanalysis) and from 1984 for solar radiation
(CERES), on a grid of 0.5° × 0.625°.
