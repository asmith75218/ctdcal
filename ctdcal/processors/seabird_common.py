#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.processors.seabird_common
:file: ctdcal/processors/seabird_common.py
:author: Allen Smith
:brief: Frequently used functions for processing Seabird sensor data
"""
import numpy as np

from ctdcal.common import json_to_obj, SensorNotFoundError


def load_all_configured_coeffs(infile):
    coeffs_dict = json_to_obj(infile)
    return coeffs_dict


def get_sensor_keys(sensor_name, coeffs):
    keys = []
    for k in coeffs.keys():
        if coeffs[k].sensor == sensor_name:
            keys.append(k)
        elif 'SensorName' in coeffs[k].coeffs:
            if coeffs[k].coeffs.SensorName == sensor_name:
                keys.append(k)
    if len(keys) == 0:
        raise SensorNotFoundError('Sensor %s not found.' % sensor_name)
    return keys


def df_raw_to_freq(raw):
    freq = raw / 256
    return freq


def df_raw_to_volts(raw):
    volt = 5 * (1 - (raw / 4095))
    return volt


def sbe3_freq_to_temp(freq, coeffs, scale=4):
    # Calibration Equation

    # The calibration yields four coefficients (g, h, i, j) that are used
    # in the following equation (Bennett):

    # T = 1 / [g + hln(f0/f) + iln2 (f0/f) + jln3 (f0/f)] - 273.15

    # where T is temperature [°C], ln is natural log function, and f is SBE 3plus output frequency [Hz]. Note that f0, an arbitrary scaling term
    # used for purposes of computational efficiency, was historically chosen as the lowest sensor frequency generated during calibration. For
    # calibration results expressed in terms of ITS-90 temperatures, f0 is set to 1000.
    g = float(coeffs.G)
    h = float(coeffs.H)
    i = float(coeffs.I)
    j = float(coeffs.J)

    f = float(coeffs['F0']) / freq

    T = 1 / (g + h * np.log(f) + i * np.log(f) ** 2 + j * np.log(f) ** 3) - 273.15
    return np.round(T, scale)


def sbe4_freq_to_cond(freq, temp, pres, coeffs, scale=4):
    #     Calibration Equation

    #     A least-squares fitting technique (including a zero conductivity point in air)
    #     yields calibration coefficients for use in the following equation:

    #     Conductivity [S/m] = (g + hf 2 + if 3 + jf 4) / (10 [1 + δt + εp])

    #     where f is SBE 4 output frequency [kHz], t is temperature [°C], p is pressure [decibars], and δ is thermal coefficient of expansion
    #     (3.25 x 10-06) and ε is bulk compressibility (-9.57 x 10-08) of the borosilicate cell. The resulting coefficients g, h, i, and j are listed on the
    #     calibration certificate.
    g = float(coeffs.G)
    h = float(coeffs.H)
    i = float(coeffs.I)
    j = float(coeffs.J)
    ctcor = float(coeffs.CTcor)
    cpcor = float(coeffs.CPcor)

    f = freq * 1.0e-3

    C = ((g + h * f ** 2 + i * f ** 3 + j * f ** 4)
         / (10 * (1 + ctcor * temp + cpcor * pres)))
    C = C * 10
    return np.round(C, scale)


def sbe9_freq_to_pres(freq, p_temp, coeffs, scale=4):
    c1 = float(coeffs.C1)
    c2 = float(coeffs.C2)
    c3 = float(coeffs.C3)
    d1 = float(coeffs.D1)
    d2 = float(coeffs.D2)
    t1 = float(coeffs.T1)
    t2 = float(coeffs.T2)
    t3 = float(coeffs.T3)
    t4 = float(coeffs.T4)
    # t5 = float(coeffs.T5)    # Not used?
    ad590m = float(coeffs.AD590M)
    ad590b = float(coeffs.AD590B)

    # Frequency in MHz...
    f = freq * 1.0e-6

    # Convert raw pressure sensor temp...
    p_temp = (ad590m * p_temp) + ad590b

    t0 = t1 + t2 * p_temp + t3 * p_temp ** 2 + t4 * p_temp ** 3
    w = 1 - t0 ** 2 * f ** 2

    P = (0.6894759
         * ((c1 + c2 * p_temp + c3 * p_temp ** 2)
            * w
            * (1 - (d1 + d2 * p_temp) * w)
            - 14.7))
    return np.round(P, scale)


def sbe43_hysteresis_voltage_1(volts, p, coeffs, sample_freq=24):
    dt = 1 / sample_freq
    D = 1 + coeffs.H1 * (np.exp(np.array(p) / coeffs.H2) - 1)
    C = np.exp(-1 * dt / coeffs.H3)

    oxy_volts = volts + coeffs.offset
    oxy_volts_new = np.zeros(oxy_volts.shape)
    oxy_volts_new[0] = oxy_volts[0]
    for i in np.arange(1, len(oxy_volts)):
        oxy_volts_new[i] = (
                                   (oxy_volts[i] + (oxy_volts_new[i - 1] * C * D[i])) - (oxy_volts[i - 1] * C)
                           ) / D[i]

    volts_corrected = oxy_volts_new - coeffs.offset

    return volts_corrected


def sbe43_hysteresis_voltage_2(t, v, p, coeffs):
    """
    Hysteresis Algorithm using Oxygen Voltage Values.
    Source: SBE Application Note 64

    D = 1 + H1 * (exponential(P( i ) / H2) – 1)
    C = exponential (-1 * (Time( i ) – Time( i-1 )) / H3)
    Oxygenvolts ( i ) = OxVolt( i ) + Voffset
    Oxnewvolts ( i ) = {( Oxygenvolts ( i ) + (Oxnewvolts ( i-1 ) * C * D)) – (Oxygenvolts ( i-1 ) * C)} / D
    Oxfinal volts ( i ) = Oxnewvolts ( i ) – Voffset

    df = pd.DataFrame(np.repeat(np.arange(2, 6),3).reshape(4,3), columns=['A', 'B', 'D'])
    new = [df.D.values[0]]
    for i in range(1, len(df.index)):
        new.append(new[i-1]*df.A.values[i]+df.B.values[i])
    df['C'] = new
    """
    D = 1 + coeffs.H1 * (np.exp(p / coeffs.H2) - 1)
    C = np.exp(-1 * (t - t.shift(1)) / coeffs.H3)
    v = v + coeffs.offset
    v_new = np.empty_like(v)
    v_new[0] = v[0]
    for i in range(1, len(v)):
        v_new[i] = ((v[i] + (v_new[i - 1] * C[i] * D[i])) - (v[i - 1] * C[i])) / D[i]
    v_new = np.array(v_new) - coeffs.offset
    return v_new
