#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.common
:file: ctdcal/common.py
:author: Allen Smith
:brief: Common code for use across ctdcal modules.
"""
import logging
import logging.config
import json
import yaml
from pathlib import Path
from importlib import resources

import pandas as pd
from munch import Munch, munchify

import ctdcal


# Defaults
BASEPATH = str(resources.files(ctdcal))
CFGFILE = Path(BASEPATH, 'cfg.yaml')


# Class definitions
class Parameters(object):
    """
    Stores a set of parameter names and values in an easy-to-access
    format from a list supplied at instantiation. Returns a munch
    (dictionary-like) object.
    """

    def __init__(self, parameters=None):
        parameters = [] if parameters is None else parameters
        self.parameters = parameters

    def create_dict(self):
        """
        Create a Bunch class object to store the parameter names for the data
        files.
        """
        bunch = Munch()

        for name in self.parameters:
            bunch[name] = []

        return bunch

    def from_csv(self, fname):
        """
        Creates a list from a csv.
        """
        lines = []
        with open(fname, 'r', encoding='utf8') as fid:
            for line in fid:
                if not line.startswith('#'):
                    lines.append(line.strip())
        return lines


# Program Error definitions
class SensorNotFoundError(Exception):
    pass


class ProgramIOError(Exception):
    pass


# Function definitions

def get_logger(module_name):
    """
    Configure logging and return the logger object.

    :param module_name: (str) name of the module that is calling the logger
    :return: logger
    """
    logger = logging.getLogger(module_name)
    log_format = "%(asctime)s | %(name)s |  %(levelname)s: %(message)s"
    formatter = logging.Formatter(log_format)
    filter = logging.Filter('ctdcal')
    # Configure logging to file...
    checkdirs(cfg.dir.log)
    file_handler = logging.FileHandler('%s/ctdcal.log' % cfg.dir.log)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    # file_handler.addFilter(filter)
    # Configure logging to screen...
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(message)s'))
    stream_handler.setLevel(logging.INFO)
    # stream_handler.addFilter(filter)

    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

def configure_logging(module_name, log_dir):
    logging_conf = yaml_to_obj(Path(BASEPATH, 'logging_conf.yml'))
    logging_conf.handlers.file.filename = Path(log_dir, logging_conf.handlers.file.filename)
    logging.config.dictConfig(logging_conf)
    logger = logging.getLogger(module_name)
    return logger

def load_user_settings(infile=CFGFILE):
    """
    Load user-defined settings
    :param infile: (str | PathLike) settings file, default cfg.yaml
    :return: dict
    """
    try:
        p = Path(infile)
    except TypeError as err:
        # not a str or PathLike object
        raise ProgramIOError('Invalid user settings filename: %s is not a string or path-like object.' % infile) from err
    if not p.exists():
        # file not found
        raise ProgramIOError('User settings file %s was not found.' % infile)
    settings = yaml_to_obj(infile)
    for d in settings.dir:
        settings.dir[d] = str(Path(settings.datadir, settings.dir[d]))
    return settings


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
    with open(infile, 'r') as f:
        data = yaml.safe_load(f)
        return munchify(data)


def get_list_indices(list_, value):
    indices = [i for i, v in enumerate(list_) if v == value]
    return indices


def checkdirs(*args):
    """
    Check for existence of one or more directories and make new if not present.

    :param args: (str | PathLike) One or more absolute directory paths.
    :return: (bool) True if directory exists, False if it cannot be created.
    """
    for dirname in args:
        try:
            p = Path(dirname)
        except TypeError as err:
            # not a str or PathLike object
            raise ProgramIOError('Cannot create the directory: %s is not a string or path-like object.' % dirname) from err
        if not p.is_absolute():
            # not an absolute path
            raise ProgramIOError('Cannot create the directory: %s is not an absolute path.' % dirname)

        try:
            p.mkdir(exist_ok=True, parents=True)
        except FileExistsError:
            # dirname exists but is not a dir
            raise ProgramIOError('Cannot create the directory: %s already exists but is not a directory.' % dirname)
    return True


# Configure user settings
cfg = load_user_settings()
