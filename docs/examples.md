# climex – Examples

This page provides practical examples of using **climex** to download and
explore the climate of Mexico.

## Basic Examples

### Example 1: Daily climate of the municipalities of a state

```python
import climex

yuc = climex.municipalities("31")
clima = climex.download_nasa_power_data(
    yuc, id_col="CVEGEO",
    parameters=["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M"],
    start_date="20240101", end_date="20241231", community="AG",
    output_folder="nasa_power_yucatan")

print(clima.shape)
print(clima.groupby("identifier")["T2M"].mean().sort_values().tail())
```

### Example 2: Monthly climate of all the country

```python
mx = climex.municipalities()
mensual = climex.download_nasa_power_data(
    mx, id_col="CVEGEO",
    parameters=["T2M", "PRECTOTCORR", "RH2M"],
    start_date="20150101", end_date="20241231",
    temporal_resolution="monthly", community="AG",
    output_folder="nasa_power_mx_monthly")
mensual.to_parquet("clima_municipios_2015_2024.parquet")
```

### Example 3: Climatology (long-term average)

```python
clim = climex.download_nasa_power_data(
    climex.municipalities("17"), id_col="CVEGEO",
    parameters=["T2M", "PRECTOTCORR"],
    temporal_resolution="climatology", output_folder="nasa_power_morelos_clim")
clim.pivot(index="identifier", columns="period", values="T2M")
```

## Advanced Examples

### Example 4: Weekly update for an early warning system

The same call with a later `end_date` and the same `output_folder` only asks
again what is new; the days not yet published come as NaN and are dropped.

```python
from datetime import date, timedelta

end = (date.today() - timedelta(days=4)).strftime("%Y%m%d")
clima = climex.download_nasa_power_data(
    climex.municipalities(), id_col="CVEGEO",
    parameters=["T2M", "RH2M", "PRECTOTCORR"],
    start_date=f"{date.today().year}0101", end_date=end,
    community="AG", output_folder=f"climatic/year_{date.today().year}")
clima = clima.dropna(subset=["T2M", "RH2M", "PRECTOTCORR"], how="all")
```

### Example 5: The AGEB of a city (with rgeomex)

```python
import rgeomex

ageb = rgeomex.extract_ageb(locality="Merida", cve_edo="31")["ageb"]
pts = climex.centroids(ageb, id_col="CVEGEO")         # a point inside each AGEB
clima = climex.download_nasa_power_data(
    pts, id_col="CVEGEO", parameters=["T2M", "PRECTOTCORR"],
    start_date="20240101", end_date="20241231", output_folder="nasa_power_merida")
```

### Example 6: Weekly series by municipality

```python
clima["week"] = clima["date"].dt.to_period("W-SAT")
semanal = (clima.groupby(["identifier", "week"])
                .agg(T2M=("T2M", "mean"), PRECTOTCORR=("PRECTOTCORR", "sum"),
                     RH2M=("RH2M", "mean"))
                .reset_index())
```

### Example 7: Plot the temperature of a municipality

```python
import matplotlib.pyplot as plt

m = clima[clima["identifier"] == "31050"]           # Mérida
ax = m.plot(x="date", y=["T2M_MIN", "T2M", "T2M_MAX"], figsize=(9, 3))
ax.set_ylabel("°C")
plt.show()
```
