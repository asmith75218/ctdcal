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

from ctdcal.common import checkdirs, load_user_settings, BASEPATH, ProgramIOError


def test_makedirs():
    testdir = 99
    # Test for invalid input
    with pytest.raises(ProgramIOError):
        checkdirs(testdir)

    testdir = 'testdir'
    # Test for a valid absolute path
    with pytest.raises(ProgramIOError):
        checkdirs(testdir)

    notadir = Path(BASEPATH, 'tests/common', 'notadir')
    notadir.touch()
    # Test if dirname exists but is not a directory
    with pytest.raises(ProgramIOError):
        checkdirs(notadir)

    testdir = Path(BASEPATH, 'tests/common', 'testdir')
    # Test that single testdir is created when it does not exist
    if testdir.exists():
        testdir.rmdir()
    checkdirs(testdir)
    assert testdir.is_dir() is True

    dirs = [Path(BASEPATH, 'tests/common', 'testdir1'), Path(BASEPATH, 'tests/common', 'testdir2')]
    for testdir in dirs:
        if testdir.exists():
            testdir.rmdir()
    checkdirs(*dirs)
    for testdir in dirs:
        assert testdir.is_dir() is True

    # clean up
    notadir.unlink()
    testdir.rmdir()


def test_load_user_settings():
    testfile = 99
    # Test for invalid input
    with pytest.raises(ProgramIOError):
        load_user_settings(testfile)

    testfile = 'foo.txt'
    with pytest.raises(ProgramIOError):
        # Test non-existant or bad filename
        load_user_settings(testfile)

    # Test for good result
    cfg = load_user_settings('common/test_cfg.yaml')
    assert cfg.foo == 'bar'
    assert cfg.baz.x == 'spam'
