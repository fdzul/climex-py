"""Download climate data of Mexico from the NASA POWER API.

NASA POWER (https://power.larc.nasa.gov) gives daily, monthly and
climatological values of temperature, precipitation, humidity, wind and
radiation for any point, from satellite and reanalysis data (MERRA-2,
CERES).
"""
from __future__ import annotations

import multiprocessing
import os
import sys
import time
from typing import Sequence

import pandas as pd
import requests

API = "https://power.larc.nasa.gov/api/temporal"
TEMPORAL = ("daily", "monthly", "climatology")
COMMUNITIES = ("RE", "AG", "SB")
FILL = -999.0          # NASA POWER missing value


def build_url(latitude: float, longitude: float, parameters: Sequence[str],
              temporal_resolution: str = "daily", community: str = "RE",
              start: str | None = None, end: str | None = None) -> str:
    """URL of one NASA POWER request for a point.

    Parameters
    ----------
    latitude, longitude : float
        Coordinates of the point (decimal degrees, WGS84).
    parameters : list of str
        NASA POWER parameters, e.g. ``["T2M", "PRECTOTCORR"]``.
    temporal_resolution : {"daily", "monthly", "climatology"}
    community : {"RE", "AG", "SB"}
    start, end : str, optional
        Dates as ``"YYYYMMDD"`` (for ``"monthly"`` only the year is used).
        Not used for ``"climatology"``.
    """
    if temporal_resolution not in TEMPORAL:
        raise ValueError(f"temporal_resolution must be one of {TEMPORAL}")
    if community not in COMMUNITIES:
        raise ValueError(f"community must be one of {COMMUNITIES}")
    if not parameters:
        raise ValueError("give at least one parameter")
    url = (f"{API}/{temporal_resolution}/point?parameters={','.join(parameters)}"
           f"&community={community}&longitude={longitude}&latitude={latitude}&format=JSON")
    if temporal_resolution == "daily":
        url += f"&start={start}&end={end}"
    elif temporal_resolution == "monthly":
        url += f"&start={str(start)[:4]}&end={str(end)[:4]}"
    return url


def parse_response(js: dict, temporal_resolution: str = "daily") -> pd.DataFrame:
    """Table (one row per day, month or period) from the JSON of NASA POWER."""
    par = js.get("properties", {}).get("parameter")
    if not par:
        msg = js.get("messages") or js.get("errors") or js.get("message") or "no data"
        raise ValueError(f"NASA POWER: {msg}")
    df = pd.DataFrame(par).replace(FILL, float("nan"))
    key = df.index.astype(str)
    df = df.reset_index(drop=True)
    if temporal_resolution == "daily":
        df.insert(0, "date", pd.to_datetime(key, format="%Y%m%d"))
    elif temporal_resolution == "monthly":
        df.insert(0, "month", key.str[4:].astype(int))
        df.insert(0, "year", key.str[:4].astype(int))
        df = df[df["month"] <= 12].reset_index(drop=True)      # 13 = annual value
    else:
        df.insert(0, "period", key)
    return df


def _download(job):
    url, filepath, info, temporal_resolution = job
    try:
        r = requests.get(url, timeout=60)
        df = parse_response(r.json(), temporal_resolution)
        for k in ("longitude", "latitude", "identifier"):
            df.insert(0, k, info[k])
        df.to_csv(filepath, index=False)
        return info, True, None
    except Exception as e:                       # noqa: BLE001 - reported per point
        return info, False, str(e)


def download_nasa_power_data(df: pd.DataFrame,
                             lat_col: str = "latitude",
                             lon_col: str = "longitude",
                             start_date: str = "20150101",
                             end_date: str = "20150305",
                             parameters: Sequence[str] = ("T2M", "T2MDEW", "T2MWET", "TS",
                                                          "T2M_RANGE", "T2M_MAX", "T2M_MIN"),
                             temporal_resolution: str = "daily",
                             community: str = "RE",
                             processes: int = 5,
                             output_folder: str = "./nasa_power_data",
                             start_col: str | None = None,
                             end_col: str | None = None,
                             id_col: str | None = None,
                             return_consolidated: bool = True,
                             verbose: bool = True) -> pd.DataFrame:
    """Download NASA POWER climate data for the points of a table.

    Each point is saved as a CSV in ``output_folder`` (``<identifier>.csv``),
    so an interrupted download can be checked point by point.

    Parameters
    ----------
    df : pandas.DataFrame
        Points to download, e.g. the centroids of the municipalities or AGEB.
    lat_col, lon_col : str
        Columns with the coordinates (decimal degrees, WGS84).
    start_date, end_date : str
        Period as ``"YYYYMMDD"``; for ``"monthly"`` only the year is used.
    parameters : list of str
        NASA POWER parameters. Temperature: ``T2M``, ``T2M_MAX``, ``T2M_MIN``,
        ``T2M_RANGE``, ``T2MDEW``, ``T2MWET``, ``TS``; precipitation:
        ``PRECTOTCORR``; humidity: ``RH2M``, ``QV2M``; wind: ``WS2M``,
        ``WS10M``; radiation: ``ALLSKY_SFC_SW_DWN``; pressure: ``PS``.
    temporal_resolution : {"daily", "monthly", "climatology"}
    community : {"RE", "AG", "SB"}
        Renewable energy, agroclimatology or sustainable buildings (units).
    processes : int
        Simultaneous requests (NASA asks for at most 5); 1 downloads in order.
    output_folder : str
        Folder for the CSV of each point.
    start_col, end_col : str, optional
        Columns with a different period for each point.
    id_col : str, optional
        Column with the identifier of each point (else ``idx_<row>``).
    return_consolidated : bool
        If True, return the data of all the points in one table; if False,
        the result of each download.
    verbose : bool
        Show the progress.

    Returns
    -------
    pandas.DataFrame
        Columns ``identifier``, ``latitude``, ``longitude``, the date
        (``date``; ``year`` and ``month``; or ``period``) and one column per
        parameter. Missing values (-999 in NASA POWER) are NaN.

    Examples
    --------
    >>> import pandas as pd
    >>> from climex import download_nasa_power_data
    >>> pts = pd.DataFrame({"id": ["merida"], "latitude": [20.97], "longitude": [-89.62]})
    >>> clima = download_nasa_power_data(pts, id_col="id", parameters=["T2M", "PRECTOTCORR"],
    ...                                  start_date="20240101", end_date="20241231")
    """
    if lat_col not in df.columns or lon_col not in df.columns:
        raise ValueError(f"df must have the columns '{lat_col}' and '{lon_col}'")
    parameters = list(parameters)
    build_url(0, 0, parameters, temporal_resolution, community, start_date, end_date)  # validate
    processes = max(1, min(int(processes), 5))
    os.makedirs(output_folder, exist_ok=True)

    jobs = []
    for idx, row in df.iterrows():
        start = pd.to_datetime(row[start_col]).strftime("%Y%m%d") if start_col else start_date
        end = pd.to_datetime(row[end_col]).strftime("%Y%m%d") if end_col else end_date
        ident = row[id_col] if id_col else f"idx_{idx}"
        info = {"index": idx, "identifier": ident, "latitude": row[lat_col],
                "longitude": row[lon_col], "filename": f"{ident}.csv",
                "start_date": None if temporal_resolution == "climatology" else start,
                "end_date": None if temporal_resolution == "climatology" else end}
        url = build_url(row[lat_col], row[lon_col], parameters, temporal_resolution,
                        community, start, end)
        jobs.append((url, os.path.join(output_folder, info["filename"]), info, temporal_resolution))

    if verbose:
        print(f"{len(jobs)} points; parameters: {', '.join(parameters)}; "
              f"{temporal_resolution}; community {community}; {processes} processes")
    t0 = time.time()
    out = []
    if processes == 1:
        it = map(_download, jobs)
        pool = None
    else:
        pool = multiprocessing.Pool(processes)
        it = pool.imap_unordered(_download, jobs)
    try:
        for i, (info, ok, err) in enumerate(it, 1):
            if verbose:
                sys.stderr.write(f"\rDownloading: {i / len(jobs):.0%}")
            out.append({**info, "success": ok, "error": err,
                        "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S")})
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    res = pd.DataFrame(out)
    if verbose:
        sys.stderr.write("\n")
        print(f"{int(res['success'].sum())}/{len(res)} points downloaded "
              f"in {time.time() - t0:.1f} s")
    if return_consolidated and res["success"].any():
        return _consolidate(res, output_folder)
    return res


def _consolidate(res: pd.DataFrame, output_folder: str) -> pd.DataFrame:
    parts = []
    for _, r in res[res["success"]].iterrows():
        d = pd.read_csv(os.path.join(output_folder, r["filename"]))
        if "date" in d.columns:
            d["date"] = pd.to_datetime(d["date"])
        parts.append(d)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
