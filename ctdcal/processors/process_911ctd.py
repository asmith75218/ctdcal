#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.processors.process_911ctd
:file: ctdcal/processors/process_911ctd.py
:author: Allen Smith
:brief: Creates a NetCDF dataset from Sea-Bird 911 CTD data as converted by CTDCAL parsers
"""
from ctdcal.processors.common import csvzip_to_df

def load_ctd(infile, columns):
    """
    Load a ctd zip
    :param infile:
    :return:
    """
    data = csvzip_to_df(infile, columns)
