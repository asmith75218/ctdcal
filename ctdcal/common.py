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

# Defaults
BASEPATH = Path.cwd()
CFGFILE = 'cfg.yaml'


class User(object):
    """
    Stores user-defined global settings as defined in a user settings file.
    The default is cfg.yaml, but can pass a custom file to override.
    """
    def __init__(self, infile=CFGFILE):
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

class ProgramIOError(Exception):
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


def makedirs(dirname):
    """
    Check for existence of one or more directories and make new if not present.

    :param dirname: (PathLike) String or path object, absolute path of a directory.
    :return: (boolean) True if directory exists, False if it cannot be created.
    """
    try:
        p = Path(dirname)
    except TypeError as err:
        # not a str or PathLike object
        raise ProgramIOError('Cannot create the directory: %s is not a string or path-like object.' % dirname) from err
    if not p.is_absolute():
        # not an absolute path
        raise ProgramIOError('Cannot create the directory: %s is not an absolute path.' % dirname)

    try:
        p.mkdir(exist_ok=True)
    except FileExistsError:
        # dirname exists but is not a dir
        raise ProgramIOError('Cannot create the directory: %s already exists but is not a directory.' % dirname)
    return True
