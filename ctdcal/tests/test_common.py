#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.tests.test_common
:file: ctdcal/tests/test_common
:author: Allen Smith
:brief: Unit tests for ctdcal.common
"""
from pathlib import Path
import pytest

# from ctdcal.common import checkdirs, check_fileexists, load_user_settings, BASEPATH, ProgramIOError
from ctdcal import common


BASEPATH = common.BASEPATH


def test_makedirs():
    testdir = 99
    # Test for invalid input
    with pytest.raises(common.ProgramIOError):
        common.checkdirs(testdir)

    testdir = 'testdir'
    # Test for a valid absolute path
    with pytest.raises(common.ProgramIOError):
        common.checkdirs(testdir)

    notadir = Path(BASEPATH, 'tests/common', 'notadir')
    notadir.touch()
    # Test if dirname exists but is not a directory
    with pytest.raises(common.ProgramIOError):
        common.checkdirs(notadir)

    testdir = Path(BASEPATH, 'tests/common', 'testdir')
    # Test that single testdir is created when it does not exist
    if testdir.exists():
        testdir.rmdir()
    common.checkdirs(testdir)
    assert testdir.is_dir() is True

    # Test case for multiple dirs
    dirs = [Path(BASEPATH, 'tests/common', 'testdir1'), Path(BASEPATH, 'tests/common', 'testdir2')]
    for testdir in dirs:
        if testdir.exists():
            testdir.rmdir()
    common.checkdirs(*dirs)
    for testdir in dirs:
        assert testdir.is_dir() is True

    # clean up
    notadir.unlink()
    for d in Path(BASEPATH, 'tests/common').glob('testdir*'):
        d.rmdir()


def test_makefiles():
    testfile = 99
    # Test for invalid input
    with pytest.raises(common.ProgramIOError):
        common.check_fileexists(testfile)

    testfile = Path(BASEPATH, 'tests/common', 'testfile')
    # Test that single testfile is created when it does not exist
    if testfile.exists():
        testfile.unlink()
    common.check_fileexists(testfile)
    assert testfile.is_file() is True

    testfiles = [Path(BASEPATH, 'tests/common', 'testfile1'), Path(BASEPATH, 'tests/common', 'testfile2')]
    for testfile in testfiles:
        if testfile.exists():
            testfile.unlink()
    common.check_fileexists(*testfiles)
    for testfile in testfiles:
        assert testfile.is_file() is True

    # clean up
    for f in Path(BASEPATH, 'tests/common').glob('testfile*'):
        f.unlink()


def test_load_user_settings():
    testfile = 99
    # Test for invalid input
    with pytest.raises(common.ProgramIOError):
        common.load_user_settings(testfile)

    testfile = 'foo.txt'
    with pytest.raises(common.ProgramIOError):
        # Test non-existant or bad filename
        common.load_user_settings(testfile)

    # Test for good result
    cfg = common.load_user_settings('common/test_cfg.yaml')
    assert cfg.foo == 'bar'
    assert cfg.baz.x == 'spam'
    assert cfg.dir.bar == '/foo/data/spam'