#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.parsers.common
:file: ctdcal/parsers/common.py
:author: Allen Smith
:brief: Provides common base classes, definitions and other utilities for all parsers.
"""
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime as dt

import pandas as pd
from munch import Munch

# Constants
NEWLINE = r'(?:\r\n|\n)?'
NMEA_TIME_BASE = 946684800

class Parameters(object):
    """Simple class to store parsed parameter names.
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


class ParserCommon(object):
    """
    Base class to prepare a calibration or data file for parsing by an individual
    instrument-specific subclass.
    """
    def __init__(self, infile, parameters=None):
        """
        Initialize with the input file and parameter names.
        """
        self.infile = infile
        if parameters is not None:
            data = Parameters(parameters)
            self.data = data.create_dict()
        else:
            self.data = None
        self.raw = None

    def load_ascii(self):
        """
        Create a buffered data object by opening the data file and reading in
        the contents
        """
        with open(self.infile, 'r') as f:
            self.raw = f.readlines()

    def load_xml(self):
        tree = ET.parse(self.infile)
        root = tree.getroot()
        self.raw = root


def nested_dict_from_xml(p, d):
    """
    Helper function for recursively parsing XML child elements into a nested
    dictionary.

    :param p: object: XML Tree iterable "parent" object
    :param d: dict
    :return: dict
    """
    for c in p:
        if not c:
            # Parent has no children, get element text and continue...
            d[c.tag] = c.text
        else:
            # Parent has a child element, call this function on a new empty
            # dict with the child now the parent...
            d[c.tag] = nested_dict_from_xml(c, dict())
    return d
