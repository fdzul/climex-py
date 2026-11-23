import json

import pandas as pd
import pytest

import climex
from climex import climex as cx

DAILY = {"properties": {"parameter": {
    "T2M": {"20240101": 22.5, "20240102": -999.0},
    "PRECTOTCORR": {"20240101": 0.0, "20240102": 3.1}}}}
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
    def __init__(self, js):
        self._js = js

    def json(self):
        return self._js


def test_download(tmp_path, monkeypatch):
    monkeypatch.setattr(cx.requests, "get", lambda url, timeout: _Resp(DAILY))
    pts = pd.DataFrame({"id": ["a", "b"], "latitude": [20.9, 19.4], "longitude": [-89.6, -99.1]})
    out = climex.download_nasa_power_data(pts, id_col="id", parameters=["T2M", "PRECTOTCORR"],
                                          start_date="20240101", end_date="20240102",
                                          processes=1, output_folder=str(tmp_path), verbose=False)
    assert len(out) == 4 and set(out["identifier"]) == {"a", "b"}
    assert (tmp_path / "a.csv").exists()
    with pytest.raises(ValueError):
        climex.download_nasa_power_data(pd.DataFrame({"x": [1]}))


def test_load_centroid_data(tmp_path):
    f = tmp_path / "c.csv"
    pd.DataFrame({"CVEGEO": ["31050", "14039"], "x": [1, 2]}).to_csv(f, index=False)
    assert len(climex.load_centroid_data(str(f), "050")) == 1
