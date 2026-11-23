# climex en español

Datos climáticos de México de la API de [NASA POWER](https://power.larc.nasa.gov):
temperatura, precipitación, humedad, viento y radiación diarios, mensuales o
climatológicos para un conjunto de puntos, por ejemplo los centroides de los
municipios, localidades o AGEB de [rgeomex](https://fdzul.github.io/rgeomex-py/).
Es la versión en Python del paquete de R climex, parte del
[dengueverse](https://fdzul.github.io/dengueverse/).

```bash
pip install git+https://github.com/fdzul/climex-py
```

Se instala como `climex-py` y se importa como `climex`.

```python
import pandas as pd
import climex

pts = pd.DataFrame({"id": ["merida"], "latitude": [20.97], "longitude": [-89.62]})
clima = climex.download_nasa_power_data(pts, id_col="id",
                                        parameters=["T2M", "PRECTOTCORR"],
                                        start_date="20240101", end_date="20241231")
```

| `temporal_resolution` | Filas |
|---|---|
| `"daily"` | una por día (`date`) |
| `"monthly"` | una por año y mes (`year`, `month`) |
| `"climatology"` | una por mes y la media anual (`period`) |

Cada punto se guarda como `<identificador>.csv` en `output_folder`. La NASA
pide como máximo 5 solicitudes simultáneas, por eso `processes` se limita a 5.
