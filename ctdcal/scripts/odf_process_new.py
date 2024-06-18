#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.scripts.odf_process_new
:file: ctdcal/scripts/odf_process_new.py
:author: Allen Smith
:brief: development script for reorg work
"""
from pathlib import Path

from ctdcal.common import load_user_settings, configure_logging, BASEPATH
from ctdcal.parsers.parse_ctd_911 import parse_all_raw


# Constants and user settings
CFGFILE = Path(BASEPATH, 'cfg.yaml')     # set the config file for this script
# cfg = load_user_settings(CFGFILE)
dirs = load_user_settings(CFGFILE).dir
CTD = 'ctd01'                            # name the CTD (used to create data dirs)

# Configure logging
# logger = get_logger('ctdcal')
logger = configure_logging('ctdcal', dirs.log)


def main():
    logger.info('----------------------------------')
    logger.info('Starting new process              ')

    # Parse raw data files to converted files
    # ---------------------------------------
    logger.info('Starting parsers...')
    # parse CTD...
    parse_all_raw(CTD, dirs.raw, dirs.cal, dirs.cfg, dirs.cnv)


    logger.info('Process finished.')


if __name__ == '__main__':
    main()