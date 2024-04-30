#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import perf_counter

from ctdcal.common import User
from ctdcal.parsers.parse_911xmlcon import parse_all_xmlcon
from ctdcal.parsers.parse_911ctd import parse_all_raw

# Constants etc. for development and testing
CFGFILE = '../cfg.yaml'
user = User(CFGFILE)
# CAST_NO = '00201'

##############################################################################
# Parse the ctd XMLCON files...
parse_all_xmlcon(user.rawdir, user.cfgdir, user.caldir)

##############################################################################
# Parse the raw ctd HEX files...
re_start = perf_counter()
parse_all_raw(user.rawdir, user.cfgdir, user.cnvdir)
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
