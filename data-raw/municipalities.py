"""Build src/climex/data/municipalities.csv: one point per municipality of
Mexico (INEGI 2019 Marco Geoestadístico, from the rgeomex GeoParquet).

Run from the root of the package:  python data-raw/municipalities.py
"""
from pathlib import Path

import rgeomex

mun = rgeomex.load("AGEM_inegi19_mx").sort_values("CVEGEO").reset_index(drop=True)
edo = rgeomex.load("AGEE_inegi19_mx")[["CVE_ENT", "NOMGEO"]].rename(columns={"NOMGEO": "state"})
g = mun.to_crs(6372)                                # projected: right centroids and areas
inside = g.representative_point().to_crs(4326)      # always inside the polygon
cent = g.centroid.to_crs(4326)                      # geometric centroid (can fall outside)
out = mun[["CVEGEO", "CVE_ENT", "CVE_MUN", "NOMGEO"]].rename(columns={"NOMGEO": "municipality"})
out = out.merge(edo, on="CVE_ENT", how="left")
out["latitude"], out["longitude"] = inside.y.round(5), inside.x.round(5)
out["centroid_lat"], out["centroid_lon"] = cent.y.round(5), cent.x.round(5)
out["centroid_inside"] = cent.to_crs(6372).within(g.geometry)
out["area_km2"] = (g.area / 1e6).round(2)
cols = ["CVEGEO", "CVE_ENT", "state", "CVE_MUN", "municipality", "latitude", "longitude",
        "centroid_lat", "centroid_lon", "centroid_inside", "area_km2"]
f = Path(__file__).resolve().parents[1] / "src" / "climex" / "data" / "municipalities.csv"
out[cols].to_csv(f, index=False)
print(f, len(out), "municipalities;", int((~out["centroid_inside"]).sum()), "centroids outside")
