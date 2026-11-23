# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## 0.2.0 (2026-11-22)

- The package is now `climex-py` (repository `fdzul/climex-py`); it is still
  imported as `climex`. The name `climex` on PyPI belongs to another project.
- Declared the dependencies (`pandas`, `requests`).
- `download_nasa_power_data()`: monthly requests use the years of the period;
  missing values (-999) are NaN; the monthly table has `year` and `month`;
  `processes=1` downloads in order; new argument `verbose`.
- Downloads run in threads instead of processes: no `if __name__ == "__main__"`
  guard is needed in scripts (on macOS and Windows the processes failed
  without it).
- Busy answers of NASA POWER (429, 5xx) are retried three times, and the
  points that still fail get a second round at the end.
- The result has only the period requested, one row per point and date (no
  duplicates), sorted by point and date; at the end it reports whether every
  point has all the period and the days without data.
- A point whose CSV in `output_folder` already has the period requested is
  not downloaded again (days not yet published, NaN, are asked again), so an
  interrupted download continues where it stopped; with a later `end_date` (an update) it is downloaded again
  (`overwrite=True` downloads everything again); repeated identifiers raise an error; the failed points
  are listed at the end.
- New `municipalities()`: one point for each of the 2,465 municipalities of
  Mexico (INEGI 2019), bundled with the package, for all the country or by
  state; built with `data-raw/municipalities.py`.
- New `centroids()`: a point inside each polygon (e.g. municipalities of
  rgeomex) ready for `download_nasa_power_data()`.
- `spatial_resolution` accepts only `"point"` (the regional API needs a
  bounding box, not a latitude and longitude); kept so the code of 0.1 runs.
- The identifiers keep their leading zeros in the result (`01001`, not `1001`).
- `load_centroid_data()` keeps the municipalities of the state given by the
  first two digits of `CVEGEO` (before it compared the last three).
- New `build_url()` and `parse_response()`; tests; documentation with mkdocs.

## 0.1.0 (2025-08-15)

- First release of `climex`.
