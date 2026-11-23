"""Points of the municipalities of Mexico, bundled with the package."""
from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

import pandas as pd


@lru_cache(maxsize=1)
def _table() -> pd.DataFrame:
    with files("climex").joinpath("data/municipalities.csv").open("r", encoding="utf-8") as f:
        return pd.read_csv(f, dtype={"CVEGEO": str, "CVE_ENT": str, "CVE_MUN": str})


def municipalities(cve_edo: str | int | list | None = None, point: str = "inside") -> pd.DataFrame:
    """One point per municipality of Mexico (INEGI 2019), all or by state.

    The table comes with the package (2,465 municipalities), so no download
    is needed; it is ready for :func:`climex.download_nasa_power_data` with
    ``id_col="CVEGEO"``.

    Parameters
    ----------
    cve_edo : str, int or list, optional
        State code(s) (``"31"``, ``31`` or ``["14", "31"]``). ``None`` returns
        the 2,465 municipalities of the country.
    point : {"inside", "centroid"}
        ``"inside"`` (default) uses a point that is always inside the
        municipality (its representative point); ``"centroid"`` uses the
        geometric centroid, which falls outside 67 curved or fragmented
        municipalities (see the column ``centroid_inside``).

    Returns
    -------
    pandas.DataFrame
        ``CVEGEO``, ``CVE_ENT``, ``state``, ``CVE_MUN``, ``municipality``,
        ``latitude``, ``longitude`` (WGS84), ``centroid_lat``,
        ``centroid_lon``, ``centroid_inside`` and ``area_km2``.

    Examples
    --------
    >>> import climex
    >>> yuc = climex.municipalities("31")          # the 106 municipalities of Yucatán
    >>> mx = climex.municipalities()               # all the country
    >>> clima = climex.download_nasa_power_data(yuc, id_col="CVEGEO",
    ...                                         parameters=["T2M", "PRECTOTCORR"],
    ...                                         start_date="20240101", end_date="20241231")
    """
    if point not in ("inside", "centroid"):
        raise ValueError('point must be "inside" or "centroid"')
    df = _table().copy()
    if cve_edo is not None:
        codes = [cve_edo] if isinstance(cve_edo, (str, int)) else list(cve_edo)
        codes = [str(c).zfill(2) for c in codes]
        bad = sorted(set(codes) - set(df["CVE_ENT"]))
        if bad:
            raise ValueError(f"state code(s) not valid (01-32): {', '.join(bad)}")
        df = df[df["CVE_ENT"].isin(codes)]
    if point == "centroid":
        df["latitude"], df["longitude"] = df["centroid_lat"], df["centroid_lon"]
    return df.reset_index(drop=True)
