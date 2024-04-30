#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: 
:file: 
:author: Allen Smith
:brief: 
"""
import json

import pandas as pd
from munch import munchify


def csvzip_to_df(infile, cols):
    df = pd.read_csv(infile, usecols=cols)
    return df


def json_to_obj(infile):
    if infile.is_file():
        with open(infile, 'r') as f:
            data = json.load(f)
            return munchify(data)
    else:
        print('File not found: %s' % str(infile))
        return None
