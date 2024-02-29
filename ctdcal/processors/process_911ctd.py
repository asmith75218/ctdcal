#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.processors.process_911ctd
:file: ctdcal/processors/process_911ctd.py
:author: Allen Smith
:brief: Creates a NetCDF dataset from Sea-Bird 911 CTD data as converted by CTDCAL parsers
"""
import re

import numpy as np
import pandas as pd
from gsw import SP_from_C

from ctdcal.common import get_list_indices
from ctdcal.processors.common import csvzip_to_df
from ctdcal.processors.seabird_common import sbe3_freq_to_temp, sbe9_freq_to_pres, sbe4_freq_to_cond


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
