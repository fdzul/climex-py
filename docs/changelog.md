# Changelog

## 0.2.0 (2026-11-22)

- The package is now `climex-py` (repository `fdzul/climex-py`); it is still
  imported as `climex`. The name `climex` on PyPI belongs to another project.
- Declared the dependencies (`pandas`, `requests`).
- `download_nasa_power_data()`: monthly requests use the years of the period;
  missing values (-999) are NaN; the monthly table has `year` and `month`;
  `processes=1` downloads in order; new argument `verbose`.
- The `spatial_resolution` argument was removed (only `"point"` was valid
  with latitude and longitude).
- New `build_url()` and `parse_response()`; tests; documentation with mkdocs.

## 0.1.0 (2025-08-15)

- First release of `climex`.
