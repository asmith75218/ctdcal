#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.common
:file: ctdcal/common.py
:author: Allen Smith
:brief: Common code for use across ctdcal modules.
"""
import json
import yaml
from pathlib import Path

import pandas as pd
from munch import Munch, munchify


class User(object):
    """
    Stores user-defined global settings as defined here.
    TODO pull settings from a file (i.e. user_settings.yaml)
    """
    def __init__(self, infile):
        cfg = yaml_to_obj(infile)
        # working directories
        self.datadir = cfg.datadir
        self.rawdir = Path(self.datadir, 'raw/')
        self.caldir = Path(self.datadir, 'cal/')
        self.cfgdir = Path(self.datadir, 'cfg/')
        self.cnvdir = Path(self.datadir, 'cnv/')
        self.procdir = Path(self.datadir, 'proc/')


class Parameters(object):
    """
    Stores a set of parameter names and values in an easy-to-access
    format from a list supplied at instantiation. Returns a munch
    (dictionary-like) object.
    """

    def __init__(self, parameters):
        self.parameters = parameters

    def create_dict(self):
        """
        Create a Munch class object to store parameter names.
        """
        munch = Munch()
        for name in self.parameters:
            munch[name] = []
        return munch


class SensorNotFoundError(Exception):
    pass


def zip_to_df(infile, cols):
    infile = Path(infile)
    if infile.is_file():
        df = pd.read_csv(infile, usecols=cols)
        return df
    else:
        print('File not found: %s' % str(infile))
        return None


def json_to_obj(infile):
    infile = Path(infile)
    if infile.is_file():
        with open(infile, 'r') as f:
            data = json.load(f)
            return munchify(data)
    else:
        print('File not found: %s' % str(infile))
        return None

def yaml_to_obj(infile):
    infile = Path(infile)
    if infile.is_file():
        with open(infile, 'r') as f:
            data = yaml.safe_load(f)
            return munchify(data)
    else:
        print('File not found: %s' % str(infile))
        return None


def get_list_indices(list_, value):
    indices = [i for i, v in enumerate(list_) if v == value]
    return indices
