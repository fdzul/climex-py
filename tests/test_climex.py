
import pandas as pd
import pytest

import climex
from climex import climex as cx

DAILY = {"properties": {"parameter": {
    "T2M": {"20240101": 22.5, "20240102": -999.0},
    "PRECTOTCORR": {"20240101": 0.0, "20240102": 3.1}}}}
FULL = {"properties": {"parameter": {
    "T2M": {"20240101": 22.5, "20240102": 23.0, "20240103": 23.4},
    "PRECTOTCORR": {"20240101": 0.0, "20240102": 3.1, "20240103": 0.2}}}}
MONTHLY = {"properties": {"parameter": {
    "T2M": {"202401": 22.0, "202402": 23.0, "202413": 26.0}}}}


def test_build_url():
    u = climex.build_url(20.97, -89.62, ["T2M", "PRECTOTCORR"], "daily", "AG", "20240101", "20241231")
    assert u.startswith("https://power.larc.nasa.gov/api/temporal/daily/point?")
    assert "parameters=T2M,PRECTOTCORR" in u and "start=20240101" in u and "community=AG" in u
    assert "start=2024&end=2025" in climex.build_url(0, 0, ["T2M"], "monthly", start="20240101", end="20251231")
    assert "start=" not in climex.build_url(0, 0, ["T2M"], "climatology")
    with pytest.raises(ValueError):
        climex.build_url(0, 0, ["T2M"], "hourly")
    with pytest.raises(ValueError):
        climex.build_url(0, 0, [], "daily")


def test_parse_response():
    d = climex.parse_response(DAILY, "daily")
    assert list(d.columns) == ["date", "T2M", "PRECTOTCORR"]
    assert d["T2M"].isna().sum() == 1
    m = climex.parse_response(MONTHLY, "monthly")
    assert list(m["month"]) == [1, 2]           # the annual value (13) is dropped
    with pytest.raises(ValueError):
        climex.parse_response({"messages": ["bad request"]})


class _Resp:
    def __init__(self, js, status=200):
        self._js, self.status_code = js, status

    def json(self):
        return self._js

    def raise_for_status(self):
        raise RuntimeError(self.status_code)


def test_download(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cx.requests, "get", lambda url, timeout: calls.append(url) or _Resp(FULL))
    pts = pd.DataFrame({"id": ["a", "b"], "latitude": [20.9, 19.4], "longitude": [-89.6, -99.1]})
    out = climex.download_nasa_power_data(pts, id_col="id", parameters=["T2M", "PRECTOTCORR"],
                                          start_date="20240101", end_date="20240102",
                                          processes=1, output_folder=str(tmp_path), verbose=False)
    assert len(out) == 4 and set(out["identifier"]) == {"a", "b"}   # only the 2 days asked
    # keys with leading zeros keep them (01001, not 1001)
    z = climex.download_nasa_power_data(pts.assign(id=["01001", "01002"]), id_col="id",
                                        parameters=["T2M"], processes=1, start_date="20240101",
                                        end_date="20240102", output_folder=str(tmp_path / "z"),
                                        spatial_resolution="point", verbose=False)
    assert set(z["identifier"]) == {"01001", "01002"}
    assert (tmp_path / "a.csv").exists()
    # run again: the points already downloaded are not requested again
    n = len(calls)
    climex.download_nasa_power_data(pts, id_col="id", parameters=["T2M"], processes=2,
                                    start_date="20240101", end_date="20240102",
                                    output_folder=str(tmp_path), verbose=False)
    assert len(calls) == n
    # a later end date (an update) downloads the points again
    climex.download_nasa_power_data(pts, id_col="id", parameters=["T2M"], processes=1,
                                    start_date="20240101", end_date="20240104",
                                    output_folder=str(tmp_path), verbose=False)
    assert len(calls) == n + 2
    with pytest.raises(ValueError, match="repeated"):
        climex.download_nasa_power_data(pd.concat([pts, pts]), id_col="id", verbose=False)
    with pytest.raises(ValueError):
        climex.download_nasa_power_data(pd.DataFrame({"x": [1]}))


def test_load_centroid_data(tmp_path):
    f = tmp_path / "c.csv"
    pd.DataFrame({"CVEGEO": ["31050", "14039", "01001"], "x": [1, 2, 3]}).to_csv(f, index=False)
    assert list(climex.load_centroid_data(str(f), "31")["CVEGEO"]) == ["31050"]
    assert list(climex.load_centroid_data(str(f), 1)["CVEGEO"]) == ["01001"]


def test_retry(monkeypatch):
    answers = iter([_Resp({}, 429), _Resp(DAILY)])
    monkeypatch.setattr(cx.requests, "get", lambda url, timeout: next(answers))
    monkeypatch.setattr(cx.time, "sleep", lambda s: None)
    assert cx._get_json("u") == DAILY


def test_centroids():
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import Polygon
    g = gpd.GeoDataFrame({"CVEGEO": ["a"]},
                         geometry=[Polygon([(-90, 20), (-89, 20), (-89, 21), (-90, 21)])], crs=4326)
    c = climex.centroids(g, "CVEGEO")
    assert list(c.columns) == ["CVEGEO", "latitude", "longitude"]
    assert 20 < c.latitude[0] < 21 and -90 < c.longitude[0] < -89


def test_municipalities():
    mx = climex.municipalities()
    assert len(mx) == 2465 and mx["CVEGEO"].is_unique
    yuc = climex.municipalities(31)
    assert len(yuc) == 106 and set(yuc["CVE_ENT"]) == {"31"}
    two = climex.municipalities(["14", "31"])
    assert set(two["CVE_ENT"]) == {"14", "31"}
    c = climex.municipalities("31", point="centroid")
    assert (c["latitude"] == c["centroid_lat"]).all()
    assert mx["latitude"].between(14, 33).all() and mx["longitude"].between(-119, -86).all()
    with pytest.raises(ValueError):
        climex.municipalities("33")


def test_no_duplicates_and_period(tmp_path, monkeypatch):
    long = {"properties": {"parameter": {"T2M": {f"202401{d:02d}": 20.0 + d for d in range(1, 11)}}}}
    monkeypatch.setattr(cx.requests, "get", lambda url, timeout: _Resp(long))
    pts = pd.DataFrame({"id": ["01001"], "latitude": [21.8], "longitude": [-102.3]})
    kw = dict(id_col="id", parameters=["T2M"], processes=1, output_folder=str(tmp_path), verbose=False)
    climex.download_nasa_power_data(pts, start_date="20240101", end_date="20240110", **kw)
    # a shorter period from the same folder: only those days, once each
    out = climex.download_nasa_power_data(pts, start_date="20240103", end_date="20240105", **kw)
    assert list(out["date"].dt.day) == [3, 4, 5]
    assert not out.duplicated(["identifier", "date"]).any()


def test_unpublished_days_are_asked_again(tmp_path, monkeypatch):
    tail = {"properties": {"parameter": {"T2M": {"20240101": 20.0, "20240102": -999.0}}}}
    calls = []
    monkeypatch.setattr(cx.requests, "get", lambda url, timeout: calls.append(1) or _Resp(tail))
    pts = pd.DataFrame({"id": ["a"], "latitude": [21.8], "longitude": [-102.3]})
    kw = dict(id_col="id", parameters=["T2M"], processes=1, start_date="20240101",
              end_date="20240102", output_folder=str(tmp_path), verbose=False)
    climex.download_nasa_power_data(pts, **kw)
    climex.download_nasa_power_data(pts, **kw)
    assert len(calls) == 2          # the NaN day makes the point be asked again
