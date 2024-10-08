[![PyPI Latest Release](https://img.shields.io/pypi/v/ctdcal.svg)](https://pypi.org/project/ctdcal/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/ctdcal.svg)](https://pypi.org/project/ctdcal/)
[![Package Status](https://img.shields.io/pypi/status/ctdcal.svg)](https://pypi.org/project/ctdcal/)
[![License](https://img.shields.io/pypi/l/ctdcal.svg)](https://github.com/cchdo/ctdcal/blob/master/LICENSE.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)


![GH Testing](https://github.com/cchdo/ctdcal/actions/workflows/run-tests.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/ctdcal/badge/?version=latest)](https://ctdcal.readthedocs.io/en/latest/?badge=latest)

# ctdcal project

The ctdcal project is a library primarily designed to process data from CTD casts and calibrate
them against Niskin bottle samples. This project is currently a work in progress and not yet
in public production.

A final public release is planned for 2025.

To contribute or try using ctdcal for yourself, feel free to install it and reach a member of the [SIO-ODF group](https://github.com/orgs/SIO-ODF/people)!

---

## Installation
ctdcal can be installed using pip:

```
$ pip install ctdcal
```

---

## CLI usage
### Initialize data folders
Initialize default `/data/` folders by running:

```
$ ctdcal init
```

(Future versions of ctdcal are planned have more robust init options/flags/etc.)

### Import and process data
To process data, copy over raw `.hex` and `.xmlcon` files into `/data/raw/` and reference data to their appropriate folder (`oxygen`, `reft`, `salt`).

Users can process their data with individual ctdcal functions or try:

```
$ ctdcal process [--group ODF]
```

to process using ODF procedures.

---

## Package usage
### Explore user settings
Most ctdcal functions get settings from `user_settings.yaml` and subsequently `config.py`. Call the configuration loader to explore default settings:

```py
from ctdcal import get_ctdcal_config
cfg = get_ctdcal_config()

# directories for I/O purposes
print(cfg.dirs)
print(cfg.fig_dirs)

# experiment-specific settings (e.g., expocode, CTD serial number) from user_settings.yaml
print(cfg.settings)

# dictionary mapping of short/long column names
print(cfg.columns)
```

As ctdcal continues to be developed, more robust [tutorials](https://ctdcal.readthedocs.io/en/latest/tutorials.html) will be added to [our documentation](https://ctdcal.readthedocs.io/en/latest/).

---

## LICENSING
BSD 3-clause
