#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import perf_counter
from ctdcal.parsers.parse_911xmlcon import parse_all_xmlcon
from ctdcal.parsers.parse_911ctd import parse_all_raw

# Constants etc. for development and testing
RAWDIR = '/Users/als026/Documents/I05/latest/data/raw/'
CALDIR = '/Users/als026/data/asmith_ctdcal/cal/'
CFGDIR = '/Users/als026/data/asmith_ctdcal/cfg/'
CNVDIR = '/Users/als026/data/asmith_ctdcal/cnv/'

# CAST_NO = '00201'

##############################################################################
# Parse the ctd XMLCON files...
parse_all_xmlcon(RAWDIR, CFGDIR, CALDIR)

##############################################################################
# Parse the raw ctd HEX files...
re_start = perf_counter()
parse_all_raw(RAWDIR, CFGDIR, CNVDIR)
re_stop = perf_counter()

print('Time regex:  %f' % (re_stop - re_start))

# Time comparisons
# none: 684.0
# zip: 871.5 (default), 799.2 (level 4), 732.8 (level 1)
# gzip: 1201.1
# xz: SLOW
# bz2:
# zst: