#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.parsers.parse_salt_odf
:file: ctdcal/parsers/parse_salt_odf.py
:author: Allen Smith
:brief: Prepare raw ODF Autosal data files for processing
"""
# TODO Separate processing out from parsing into new processing module
import csv
import io
import logging
from pathlib import Path

import gsw
import numpy as np
import pandas as pd

from ctdcal.common import BASEPATH, check_fileexists, checkdirs

FLAGFILE = Path(BASEPATH, 'flags_manual_salt.csv')

logger = logging.getLogger(__name__)

def _salt_loader(filename, flag_file=FLAGFILE):
    """
    Load raw file into salt and reference DataFrames.
    """
    check_fileexists(flag_file)
    csv_opts = dict(delimiter=" ", quoting=csv.QUOTE_NONE, skipinitialspace="True")
    if isinstance(filename, (str, Path)):
        with open(filename, newline="") as f:
            saltF = csv.reader(f, **csv_opts)
            saltArray = [row for row in saltF]
            ssscc = Path(filename).stem
    elif isinstance(filename, io.StringIO):
        saltF = csv.reader(filename, **csv_opts)
        saltArray = [row for row in saltF]
        ssscc = "test_odf_io"
    else:
        raise NotImplementedError(
            "Salt loader only able to read in str, Path, or StringIO classes"
        )

    del saltArray[0]  # remove file header
    saltDF = pd.DataFrame.from_records(saltArray)

    cols = dict(  # having this as a dict streamlines next steps
        [
            ("STNNBR", int),
            ("CASTNO", int),
            ("SAMPNO", int),
            ("BathTEMP", int),
            ("CRavg", float),
            ("autosalSAMPNO", int),
            ("Unknown", int),
            ("StartTime", object),
            ("EndTime", object),
            ("Attempts", int),
        ]
    )

    # add as many "Reading#"s as needed
    for ii in range(0, len(saltDF.columns) - len(cols)):
        cols["Reading{}".format(ii + 1)] = float
    saltDF.columns = list(cols.keys())  # name columns

    # TODO: check autosalSAMPNO against SAMPNO for mismatches?
    # TODO: handling for re-samples?

    # check for commented out lines
    commented = saltDF["STNNBR"].str.startswith(("#", "x"))
    if commented.any():
        logger.debug(f"Found comment character (#, x) in {ssscc} salt file, ignoring line")
        saltDF = saltDF[~commented]

    # check end time for * and code questionable
    # (unconfirmed but * appears to indicate a lot of things from LabView code:
    # large spread in values, long time between samples, manual override, etc.)
    flagged = saltDF["EndTime"].str.contains("*", regex=False)
    if flagged.any():
        # remove asterisks from EndTime and flag samples
        logger.debug(f"Found * in {ssscc} salt file, flagging value(s) as questionable")
        saltDF["EndTime"] = saltDF["EndTime"].str.strip("*")
        questionable = pd.DataFrame()
        questionable["SAMPNO"] = saltDF.loc[flagged, "SAMPNO"].astype(int)
        questionable.insert(0, "SSSCC", ssscc)
        questionable["diff"] = np.nan
        questionable["salinity_flag"] = 3
        questionable["comments"] = "Auto-flagged by processing function (had * in row)"
        questionable.to_csv(flag_file, mode="a+", index=False, header=None)

    # add time (in seconds) needed for autosal drift removal step
    saltDF["IndexTime"] = pd.to_datetime(saltDF["EndTime"])
    saltDF["IndexTime"] = (saltDF["IndexTime"] - saltDF["IndexTime"].iloc[0]).dt.seconds
    saltDF["IndexTime"] += (saltDF["IndexTime"] < 0) * (3600 * 24)  # fix overnight runs

    refDF = saltDF.loc[
        saltDF["autosalSAMPNO"] == "worm", ["IndexTime", "CRavg"]
    ].astype(float)
    saltDF = saltDF[saltDF["autosalSAMPNO"] != "worm"].astype(cols)  # force dtypes

    return saltDF, refDF


def remove_autosal_drift(saltDF, refDF):
    """Calculate linear CR drift between reference values"""
    if refDF.shape != (2, 2):
        ssscc = f"{saltDF['STNNBR'].unique()[0]:03d}{saltDF['CASTNO'].unique()[0]:02d}"
        logger.warning(
            f"Failed to find start/end reference readings for {ssscc}, check salt file"
        )
    else:
        # find rate of drift
        diff = refDF.diff(axis="index").dropna()
        time_coef = (diff["CRavg"] / diff["IndexTime"]).iloc[0]

        # apply offset as a linear function of time
        saltDF = saltDF.copy(deep=True)  # avoid modifying input dataframe
        saltDF["CRavg"] += saltDF["IndexTime"] * time_coef
        saltDF["CRavg"] = saltDF["CRavg"].round(5)  # match initial precision

    return saltDF.drop(labels="IndexTime", axis="columns")


def _salt_exporter(saltDF, outdir, stn_col="STNNBR", cast_col="CASTNO"):
    """
    Export salt DataFrame to .csv file. Extra logic is included in the event that
    multiple stations and/or casts are included in a single raw salt file.
    """
    stations = saltDF[stn_col].unique()
    for station in stations:
        stn_salts = saltDF[saltDF[stn_col] == station]
        casts = stn_salts[cast_col].unique()
        for cast in casts:
            stn_cast_salts = stn_salts[stn_salts[cast_col] == cast].copy()
            stn_cast_salts.dropna(axis=1, how="all", inplace=True)  # drop empty columns
            outfile = Path(outdir) / f"{station:03.0f}{cast:02.0f}_salts.csv"  # SSSCC_*
            if outfile.exists():
                logger.debug(str(outfile) + " already exists...skipping")
                continue
            stn_cast_salts.to_csv(outfile, index=False)


def parse_all_salts(indir, outdir):
    """
    Parse all salt files in a given directory into csv files for processing.

    :param indir: (str or path-like) input directory
    :param outdir: (str or path-like) output directory
    """
    indir = Path(indir)
    outdir = Path(outdir)
    checkdirs(indir, outdir)
    salt_files = [f for f in indir.iterdir() if f.suffix == '' and f.is_file()]

    for salt_file in salt_files:
        ssscc = salt_file.stem
        if (outdir / f"{ssscc}_salts.csv").exists():
            logger.debug(f"{ssscc}_salts.csv already exists in {outdir.name}... skipping")
            continue
        else:
            try:
                saltDF, refDF = _salt_loader(Path(indir) / ssscc)
            except FileNotFoundError:
                logger.warning(f"Salt file for cast {ssscc} does not exist... skipping")
                continue
            saltDF = remove_autosal_drift(saltDF, refDF)
            saltDF["SALNTY"] = gsw.SP_salinometer(
                (saltDF["CRavg"] / 2.0), saltDF["BathTEMP"]
            )  # .round(4)
            _salt_exporter(saltDF, outdir)
