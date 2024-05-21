#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.parsers.test.test_ctd_911
:file: ctdcal/parsers/test/test_ctd_911.py
:author: Allen Smith
:brief: Unit tests for ctdcal.parsers.parse_ctd_911
"""
from pathlib import Path

from ctdcal.parsers.parse_ctd_911 import parse_all_raw

def test_parse_all_raw():
    instr = '01'
    indir = Path('ctd_911/raw').resolve()
    cfgdir = Path('ctd_911/cfg').resolve()
    caldir = Path('ctd_911/cal').resolve()
    outdir = Path('ctd_911/cnv').resolve()

    parse_all_raw(instr, indir, cfgdir, caldir, outdir)
    # Test if xmlcon files are parsed to json in cfg dir
    outfiles = list(Path(cfgdir, instr).glob('*.json'))
    assert len(outfiles) == 2
    # clean up as we go...
    for f in outfiles:
        f.unlink()
    # Test if xmlcon files are parsed to json in cal dir
    outfiles = list(Path(caldir, instr).glob('*.json'))
    assert len(outfiles) == 2
    # clean up as we go...
    for f in outfiles:
        f.unlink()

    # Test that output files are saved in cnv dir
    outfiles = list(Path(outdir, instr).glob('*.zip'))
    assert len(outfiles) == 2
    # clean up as we go...
    for f in outfiles:
        f.unlink()

    # clean up empty test dirs...
    Path(cfgdir, instr).rmdir()
    Path(caldir, instr).rmdir()
    Path(outdir, instr).rmdir()
