#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import perf_counter
from pathlib import Path

from ctdcal.common import load_user_settings, BASEPATH
from ctdcal.parsers.extras.parse_ctd_911xmlcon import parse_all_xmlcon
from ctdcal.parsers.parse_ctd_911 import parse_all_raw

# Constants etc. for development and testing
CFGFILE = Path(BASEPATH, 'cfg.yaml')
cfg = load_user_settings(CFGFILE)
CTD = 'ctd01'
# CAST_NO = '00201'

##############################################################################
# Parse the ctd XMLCON files...
# parse_all_xmlcon(cfg.dir.raw, cfg.dir.cfg, cfg.dir.cal)

##############################################################################
# Parse the raw ctd HEX files...
re_start = perf_counter()
parse_all_raw(CTD, cfg.dir.raw, cfg.dir.cal, cfg.dir.cfg, cfg.dir.cnv)
re_stop = perf_counter()

print('Parse time:  %f' % (re_stop - re_start))

# Time comparisons
# none: 684.0
# zip: 871.5 (default), 799.2 (level 4), 732.8 (level 1)
# gzip: 1201.1
# xz: SLOW
# bz2:
# zst:

##############################################################################
# Process the converted ctd files...
# re_start = perf_counter()
# process_all_core(user.rawdir, user.caldir, user.cfgdir, user.procdir)
# re_stop = perf_counter()
#
# print('Core process time:  %f' % (re_stop - re_start))
