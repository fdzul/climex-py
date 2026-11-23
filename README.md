# climex <img src="docs/assets/logo.png" align="right" height="139" alt="" />

**English** | [Español](#español)

Climate data of Mexico from the NASA POWER API: daily, monthly or
climatological temperature, precipitation, humidity, wind and radiation for a
set of points (for example the centroids of municipalities, localities or
AGEB). It is the Python version of the R package climex, part of the
[dengueverse](https://fdzul.github.io/dengueverse/).

## Installation

```bash
pip install git+https://github.com/fdzul/climex-py
```

The package is installed as `climex-py` and imported as `climex`.

## Usage

```python
import pandas as pd
import climex

pts = pd.DataFrame({"id": ["merida", "guadalajara"],
                    "latitude": [20.97, 20.67],
                    "longitude": [-89.62, -103.35]})

clima = climex.download_nasa_power_data(
    pts, id_col="id",
    parameters=["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M"],
    start_date="20240101", end_date="20241231",
    temporal_resolution="daily", community="AG")
```

The result has one row per point and day (`identifier`, `latitude`,
`longitude`, `date` and one column per parameter). With
`temporal_resolution="monthly"` the rows are per year and month, and with
`"climatology"` per month of the long-term average.

Documentation: <https://fdzul.github.io/climex-py/>

## License

MIT.

---

## Español

Datos climáticos de México de la API de NASA POWER: temperatura,
precipitación, humedad, viento y radiación diarios, mensuales o
climatológicos para un conjunto de puntos (por ejemplo, los centroides de
municipios, localidades o AGEB). Es la versión en Python del paquete de R
climex, parte del [dengueverse](https://fdzul.github.io/dengueverse/).

```bash
pip install git+https://github.com/fdzul/climex-py
```

```python
import climex
clima = climex.download_nasa_power_data(pts, id_col="id",
                                        parameters=["T2M", "PRECTOTCORR"],
                                        start_date="20240101", end_date="20241231")
```
