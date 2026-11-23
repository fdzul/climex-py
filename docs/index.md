# climex <img src="assets/logo.png" align="right" width="130" style="width:130px" alt="" />

Climate data of Mexico from the [NASA POWER](https://power.larc.nasa.gov) API:
daily, monthly or climatological temperature, precipitation, humidity, wind and
radiation for a set of points, for example the centroids of the
municipalities, localities or AGEB of [rgeomex](https://fdzul.github.io/rgeomex-py/).
It is the Python version of the R package climex, part of the
[dengueverse](https://fdzul.github.io/dengueverse/).

```bash
pip install git+https://github.com/fdzul/climex-py
```

```python
import pandas as pd
import climex

pts = pd.DataFrame({"id": ["merida"], "latitude": [20.97], "longitude": [-89.62]})
clima = climex.download_nasa_power_data(pts, id_col="id",
                                        parameters=["T2M", "PRECTOTCORR"],
                                        start_date="20240101", end_date="20241231")
```

See [Getting Started](getting-started.md) for the parameters, the temporal
resolutions and an example with the municipalities of a state.
