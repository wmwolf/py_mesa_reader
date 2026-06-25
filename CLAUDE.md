# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`mesa_reader` is a small, single-module Python library for reading and manipulating
output files from [MESA](https://mesastar.org/) (Modules for Experiments in Stellar
Astrophysics). It is published to PyPI as `mesa-reader`. The only runtime dependency
is `numpy`.

## Commands

```console
pip install .                  # install the package locally
pip install -r requirements-dev.txt   # install dev tools (ruff, pytest)

ruff format --check            # lint: formatting check (run before committing)
ruff check                     # lint: static checks
pytest                         # run the test suite
pytest path/to/test.py::name   # run a single test

make html                      # build Sphinx docs into docs_build/ (also: bash make_docs.sh)
```

CI (`.github/workflows/test-package.yml`) runs `ruff format --check`, `ruff check`,
and `pytest` on Python 3.12 and 3.13. Tests and fixtures live under `tests/`.

The published HTML docs live in `docs/`; the reStructuredText sources are in
`docs_source/`. Docs are rebuilt from docstrings and deployed to GitHub Pages by
`.github/workflows/docs.yml` on each release (not on every push), so docstring
changes only reach the live site when a new version is released. `build/`, `dist/`,
and `*.egg-info/` are build artifacts.

## Architecture

All code lives in [`mesa_reader/__init__.py`](mesa_reader/__init__.py) — three classes
that build on each other:

- **`MesaData`** — the core file reader. Reads a single MESA log file (history or
  profile, `.data`/`.log`) or a saved model (`.mod`). File type is auto-detected from
  the extension. Log files are parsed with `pandas.read_csv` (fast C parser) and
  then converted to a numpy structured array (`bulk_data`) plus a header dict;
  `.mod` files use a hand-rolled line walker (`read_model_data`) that converts
  Fortran `D`-exponent notation to Python floats. History files are scrubbed of
  backups/restarts so `model_number` is monotonic (`remove_backups`).

- **`MesaProfileIndex`** — parses `profiles.index` (also via `pandas.read_csv`),
  providing the profile-number ↔ model-number mapping.

- **`MesaLogDir`** — ties a whole LOGS directory together: it owns one `MesaData`
  history object plus a `MesaProfileIndex`, and lazily constructs (and optionally
  memoizes) per-profile `MesaData` objects via `profile_data`.

### Key conventions to preserve

- **Attribute access falls through to data lookup.** Both `MesaData` and
  `MesaProfileIndex` override `__getattr__`, so `m.star_age` is equivalent to
  `m.data('star_age')` (and falls back to `header(...)`). When adding methods or
  attributes, be aware that any unknown attribute is routed to the data accessor.

- **Logarithm/linear key inference.** `MesaData.data(key)` does more than a dict
  lookup: if `key` is absent it searches for a `log_`/`ln_` variant and exponentiates
  it (or vice-versa) via the `_log_version`/`_ln_version`/`_exp10_version`/
  `_exp_version` helpers. Preserve this fallback chain when touching `data`.

- **Parsing layout is configurable via class methods.** `header_names_line`,
  `bulk_names_line` (on `MesaData`) and `index_start_line`/`index_names` (on
  `MesaProfileIndex`) are class-level and set through classmethods like
  `set_data_rows`. Changing them affects all subsequent reads.

- **Header/model values are parsed with `eval`.** `read_log_data` and
  `read_model_data` call `eval` on tokens from the file. This is intentional for
  reading numeric/string MESA output; keep input assumed to be trusted MESA files.

- **pandas parses, numpy holds and computes.** File ingestion uses
  `pandas.read_csv` for speed, but the in-memory data (`bulk_data`, the arrays
  returned by `data()` and `MesaProfileIndex.data()`) are numpy, and array math
  (`np.exp`/`np.log10`, `np.where`, `np.minimum.accumulate`) stays in numpy. This
  split is deliberate — numpy is pandas' own dependency, and the numpy-array
  return type is the public API contract. Don't convert these to DataFrames/Series.
