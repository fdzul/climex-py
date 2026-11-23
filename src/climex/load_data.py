import pandas as pd


def load_centroid_data(path: str, state: str) -> pd.DataFrame:
    """Read a CSV of municipal points and keep the municipalities of one state.

    Parameters
    ----------
    path : str
        CSV with a ``CVEGEO`` column (municipality key, 5 digits).
    state : str
        State code, e.g. ``"01"`` (the first two digits of ``CVEGEO``).

    Notes
    -----
    :func:`climex.municipalities` gives the same points for all the
    municipalities of Mexico without a CSV.
    """
    df = pd.read_csv(path, dtype={"CVEGEO": str})
    cve = df["CVEGEO"].str.zfill(5)
    return df[cve.str[:2] == str(state).zfill(2)].reset_index(drop=True)


def centroids(gdf, id_col: str) -> pd.DataFrame:
    """Points (inside each polygon) to download the climate of polygons.

    Uses the representative point of each polygon, which is always inside it
    (the centroid of a curved municipality can fall outside).

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        Polygons, e.g. ``rgeomex.load("AGEM_inegi19_mx", cve_edo="31")``.
    id_col : str
        Column with the identifier of each polygon (e.g. ``"CVEGEO"``).

    Returns
    -------
    pandas.DataFrame
        ``id_col``, ``latitude`` and ``longitude`` (WGS84), ready for
        :func:`climex.download_nasa_power_data`.
    """
    crs = gdf.crs
    g = gdf.to_crs(6372) if crs is not None and crs.is_geographic else gdf
    pts = g.representative_point()
    pts = pts.to_crs(4326) if pts.crs is not None else pts
    return pd.DataFrame({id_col: gdf[id_col].to_numpy(),
                         "latitude": pts.y.round(5).to_numpy(),
                         "longitude": pts.x.round(5).to_numpy()})
