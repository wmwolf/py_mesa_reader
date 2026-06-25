[![Repo Status][status-badge]][status-link]
[![PyPI Version Status][pypi-badge]][pypi-link]
[![Test Status][workflow-test-badge]][workflow-test-link]
[![Readthedocs Status][docs-badge]][docs-link]
[![License][license-badge]][license-link]

[status-link]:         https://www.repostatus.org/#active
[status-badge]:        https://www.repostatus.org/badges/latest/active.svg
[pypi-link]:           https://pypi.org/project/mesa-reader
[pypi-badge]:          https://img.shields.io/pypi/v/mesa-reader?label=PyPI&logo=pypi
[workflow-test-link]:  https://github.com/wmwolf/py_mesa_reader/actions/workflows/test-package.yml
[workflow-test-badge]: https://github.com/wmwolf/py_mesa_reader/actions/workflows/test-package.yml/badge.svg?event=push
[docs-link]:           https://billwolf.space/py_mesa_reader
[docs-badge]:          https://github.com/wmwolf/py_mesa_reader/actions/workflows/docs.yml/badge.svg
[license-link]:        https://opensource.org/license/lgpl-3-0
[license-badge]:       https://img.shields.io/badge/license-LGPLv3-blue.svg

# mesa_reader

A Python package for easily accessing and manipulating output of the [Modules for Experiments in Stellar Astrophysics (MESA)](https://mesastar.org/) code.


## Installation

The easiest way to install the package is via `pip`:

```console
pip install mesa_reader
```

You can also install by cloning or downloading this repository, `cd` into it and then execute

```console
python setup.py install
```

or

```console
pip install .
```
    
to install the package on your system.


## Uninstallation

Uninstall the package by executing

```console
pip uninstall mesa_reader
```


## Usage

Start using the package in your Python scripts by first importing it:

```python
import mesa_reader as mr
```

Complete documentation on the `mesa_reader` module found
[here](https://wmwolf.github.io/py_mesa_reader).
