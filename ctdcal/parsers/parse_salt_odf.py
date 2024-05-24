#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.parsers.parse_salt_odf
:file: ctdcal/parsers/parse_salt_odf.py
:author: Allen Smith
:brief: Prepare raw ODF Autosal data files for processing
"""
from pathlib import Path

from ctdcal.common import BASEPATH

FLAGFILE = Path(BASEPATH, 'flags_manual_salt.csv')

