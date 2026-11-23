import pandas as pd


def load_centroid_data(path: str, state: str) -> pd.DataFrame:
    """Read a CSV of centroids and keep the rows of one state.

    Parameters
    ----------
    path : str
        CSV with a ``CVEGEO`` column.
    state : str
        Last three characters of ``CVEGEO`` that identify the rows to keep.
    """
    df = pd.read_csv(path, dtype={"CVEGEO": str})
    return df[df["CVEGEO"].str[-3:] == state].reset_index(drop=True)


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
