#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.processors.process_911ctd
:file: ctdcal/processors/process_911ctd.py
:author: Allen Smith
:brief: Creates a NetCDF dataset from Sea-Bird 911 CTD data as converted by CTDCAL parsers
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from gsw import SP_from_C

from ctdcal.common import get_list_indices, Settings
from ctdcal.processors.common import csvzip_to_df, json_to_obj
from ctdcal.processors.seabird_common import sbe3_freq_to_temp, sbe9_freq_to_pres, sbe4_freq_to_cond, sbe_raw_to_freq, sbe_raw_to_volts


class Processor(object):
    """
    Store calibration and configuration parameters used to process
    a cast.
    """
    def __init__(self, cfgfile, calfile):
        self.cfg = json_to_obj(cfgfile)
        self.sensors = json_to_obj(calfile)
        self.num_freq = 5 - int(self.cfg.cc_voltage_channels_sup)
        self.num_volts = 8 - int(self.cfg.cc_voltage_channels_sup)
        self.columns_f = ['freq%s' % i for i in range(self.num_freq)]
        self.columns_v = ['v%s' % i for i in range(self.num_volts)]
        self.columns_etc = ['systime', 'p_temp', 'nmea_lat', 'nmea_lon', 'nmea_signs_status']
        self.columns_all = self.columns_f + self.columns_v + self.columns_etc

def df_process_freq_sensors(raw_data, coeff_dict, processed_data):
    # Extract sensor names from the coeffs file
    sensor_names = [coeff_dict[str(i)]['sensor'] for i in range(len(coeff_dict))]

    # Process all SBE3 temperature sensors...
    indices = get_list_indices(sensor_names, 'TemperatureSensor')
    # There should be at least one temperature sensor found
    if len(indices) >= 1:
        for i, idx in enumerate(indices):
            coeffs = coeff_dict[str(idx)].coeffs
            # Convert frequencies to temperatures using the Sea-Bird
            # equation
            column = sbe3_freq_to_temp(raw_data['freq%s' % idx], coeffs)
            # Add results to the processed data
            processed_data['CTDTMP%s' % (i + 1)] = column
    else:
        # If no temperature sensors were found, we have a problem
        # Note this won't catch if there are more than two sensors,
        # which should be an impossible occurance unless someone
        # has manipulated a coeffs file.
        # TODO: Do something appropriate about it
        print('No SBE3 sensors found in coeffs file, skipping.')

    # Process SBE9 pressure sensor...
    indices = get_list_indices(sensor_names, 'PressureSensor')
    if len(indices) == 1:  # There can be only one...
        coeffs = coeff_dict[str(indices[0])].coeffs
        # Convert frequencies to pressure using the Sea-Bird
        # equation
        column = sbe9_freq_to_pres(raw_data['freq%s' % indices[0]], raw_data['p_temp'], coeffs)
        # Add results to the processed data
        processed_data['CTDPRS'] = column
    else:
        # If no pressure sensor was found (or too many), we have
        # a problem
        # TODO: Do something appropriate about it
        print('Found %s SBE9 sensors in coeffs file, skipping.')

    # Process SBE4 conductivity sensors...
    indices = get_list_indices(sensor_names, 'ConductivitySensor')
    # There should be at least one temperature sensor found
    if len(indices) >= 1:
        for i, idx in enumerate(indices):
            coeffs = coeff_dict[str(idx)].coeffs.Coefficients
            # Convert frequencies to conductivity using the Sea-Bird
            # equation
            column = sbe4_freq_to_cond(raw_data['freq%s' % idx], processed_data['CTDTMP%s' % (i + 1)],
                                       processed_data['CTDPRS'], coeffs)
            # Add results to the processed data
            processed_data['CTDCOND%s' % (i + 1)] = column
    else:
        # If no conductivity sensors were found, we have a problem
        # Note this won't catch if there are more than two sensors,
        # which should be an impossible occurance unless someone
        # has manipulated a coeffs file.
        # TODO: Do something appropriate about it
        print('No SBE4 sensors found in coeffs file, skipping.')

    return processed_data


def process_ps(data):
    pattern = re.compile('cond([0-9]+)')
    for column in data.columns:
        match = re.search(pattern, column.lower())
        if match:
            data['CTDSAL%s' % match.group(1)] = SP_from_C(data[column],
                                                          data['CTDTMP%s' % match.group(1)],
                                                          data['CTDPRS'])
    return data


def process_nmea_latlon(raw_data):
    data = pd.DataFrame()
    latsign = np.where((raw_data['nmea_signs_status'] & 128), -1, 1)
    lonsign = np.where((raw_data['nmea_signs_status'] & 64), -1, 1)

    data['lat'] = raw_data['nmea_lat'] / 50000 * latsign
    data['lon'] = raw_data['nmea_lon'] / 50000 * lonsign
    data['new_fix'] = (raw_data['nmea_signs_status'] & 1).astype(bool)
    return data


def process_cast(infile):
    user = Settings()
    cast_no = infile.stem[:5]
    cfgfile = Path(user.cfgdir, '%s_config.json' % cast_no)
    calfile = Path(user.caldir, '%s_coeffs.json' % cast_no)
    print("Loading cast %s converted data..." % cast_no)
    cast = Processor(cfgfile, calfile)
    cnv = csvzip_to_df(infile, cast.columns_all)
    # convert raw counts to freqs
    cnv.loc[:, cast.columns_f] = sbe_raw_to_freq(cnv[cast.columns_f])

    processed_data = pd.DataFrame()
    # Timestamps don't need processing right now, just paste 'em in...
    processed_data['scan_datetime'] = cnv['systime']

    # Process the freq sensors
    processed_data = df_process_freq_sensors(cnv, cast.sensors, processed_data)

    # Process and add columns for practical salinity
    processed_data = process_ps(processed_data)

    # Process NMEA lat/lon if present...
    if cast.cfg.cc_has_nmea_latlon:
        gps = process_nmea_latlon(cnv[['nmea_lat', 'nmea_lon', 'nmea_signs_status']])
        processed_data[['lat', 'lon', 'new_fix']] = gps

    return processed_data, cast_no


def process_all_core(indir, outdir, ext='zip'):
    """
    Process data from engineering units into science units for all core SBE911
    CTD sensors. Includes pressure, one or two temperature and one or two
    conductivity as well as system time, and NMEA data if present.

    :param indir: Path or path-like object. Converted cast file directory.
    :param ext: string. File extension of converted cast files. Defaults to 'zip'.
    :return: None
    """
    indir = Path(indir)
    cast_files = [fname for fname in sorted(list(indir.glob('*_cnv.%s' % ext)))]
    for cast_file in cast_files:
        cast, cast_no = process_cast(cast_file)
        outfile = Path(outdir, '%s_cnv.zip' % cast_no)
