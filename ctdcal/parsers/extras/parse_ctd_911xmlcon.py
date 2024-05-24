#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.parsers.parse_911xmlcon
:file: ctdcal/parsers/parse_ctd_911xmlcon.py
:author: Allen Smith
:brief: Parses XML configuration files for Sea-Bird 911 CTD instruments.
"""
# TODO: Add packages to project requirements
import logging
from pathlib import Path

from munch import Munch

from ctdcal.parsers.common import ParserCommon, nested_dict_from_xml


logger = logging.getLogger(__name__)


class Parser(ParserCommon):
    """
    Extension of base parser class to parse instrument-specific metadata
    and calibration coefficients from a Sea-Bird 911 xmlcon file.
    Includes methods to export configs and coeffs to JSON.
    """
    def __init__(self, infile):
        parameter_names = ['cc_frequency_channels_sup',
                           'cc_voltage_channels_sup',
                           'cc_has_surfacepar',
                           'cc_has_nmea_latlon',
                           'cc_has_nmea_depth',
                           'cc_has_nmea_time',
                           'cc_has_time',
                           'cc_sensors']
        self.cal_coeffs = Munch()
        super().__init__(infile, parameter_names)

    def parse_xml(self):
        instrument = self.raw[0]
        self.data.cc_frequency_channels_sup = instrument.find('FrequencyChannelsSuppressed').text
        self.data.cc_voltage_channels_sup = instrument.find('VoltageWordsSuppressed').text
        self.data.cc_has_surfacepar = instrument.find('SurfaceParVoltageAdded').text
        self.data.cc_has_nmea_latlon = instrument.find('NmeaPositionDataAdded').text
        self.data.cc_has_nmea_depth = instrument.find('NmeaDepthDataAdded').text
        self.data.cc_has_nmea_time = instrument.find('NmeaTimeAdded').text
        self.data.cc_has_time = instrument.find('ScanTimeAdded').text
        self.data.cc_sensors = [sensor.attrib for sensor in self.raw.iter('Sensor')]

    def parse_cal_coeffs(self):
        sensors = self.raw.findall('.//Sensor')
        for sensor in sensors:
            sensor_dict = nested_dict_from_xml(sensor, dict())
            sensor_type, sensor_coeffs = [item for item in sensor_dict.items()].pop()
            self.cal_coeffs[sensor.attrib['index']] = Munch({'sensor': sensor_type,
                                                             'coeffs': sensor_coeffs})

    def config_to_json(self, outdir, cast_no):
        outfile = Path(outdir, '%s_config.json' % cast_no)
        with open(outfile, 'w') as f:
            f.write(self.data.toJSON())

    def coeffs_to_json(self, outdir, cast_no):
        outfile = Path(outdir, '%s_coeffs.json' % cast_no)
        with open(outfile, 'w') as f:
            f.write(self.cal_coeffs.toJSON())


def parse_all_xmlcon(name, indir, cfgdir, caldir, ext='XMLCON'):
    """
    Function to parse all XMLCON files in a directory and save as individual
    JSON files with configuration settings and calibration coeffs.

    :param name: (str) instrument name
    :param indir: path of input directory
    :param cfgdir: path of configuration output directory
    :param caldir: path of calibration output directory
    :param ext: (str) filename extension. Defaults to XMLCON.
    :return: None
    """
    p = Path(indir, name)
    print("searching in %s..." % str(p))
    cast_files = [fname for fname in list(p.glob('*.%s' % ext))]
    for cast_file in cast_files:
        cast_no = cast_file.stem
        print("Importing cast %s configuration data..." % cast_no)
        cast = Parser(cast_file)
        cast.load_xml()
        cast.parse_xml()
        cast.parse_cal_coeffs()

        print("Exporting cast %s config..." % cast_no)
        cast.config_to_json(cfgdir, cast_no)

        print("Exporting cast %s coeffs..." % cast_no)
        cast.coeffs_to_json(caldir, cast_no)


def parse_xmlcon(infile, cfgdir, caldir):
    """
    Function to parse a single xmlcon file. Otherwise like above.

    :param infile: path of input file
    :param cfgdir: path of configuration output directory
    :param caldir: path of calibration output directory
    :return: None
    """
    p = Path(infile)
    cast_no = p.stem
    logger.info("Importing cast %s configuration data..." % cast_no)
    cast = Parser(p)
    cast.load_xml()
    cast.parse_xml()
    cast.parse_cal_coeffs()

    logger.info("Exporting cast %s config..." % cast_no)
    cast.config_to_json(cfgdir, cast_no)

    logger.info("Exporting cast %s coeffs..." % cast_no)
    cast.coeffs_to_json(caldir, cast_no)
