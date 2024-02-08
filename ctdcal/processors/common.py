#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: 
:file: 
:author: Allen Smith
:brief: 
"""
import pandas as pd

def csvzip_to_df(infile, cols):
    df = pd.DataFrame.read_csv(infile, usecols=cols)
    return df
