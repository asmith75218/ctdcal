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

from ctdcal.common import makedirs, BASEPATH, ProgramIOError


def test_makedirs():
    testdir = 99
    # Test for invalid input
    with pytest.raises(ProgramIOError):
        makedirs(testdir)

    testdir = 'testdir'
    # Test for a valid absolute path
    with pytest.raises(ProgramIOError):
        makedirs(testdir)

    notadir = Path(BASEPATH, 'common', 'notadir')
    notadir.touch()
    # Test if dirname exists but is not a directory
    with pytest.raises(ProgramIOError):
        makedirs(notadir)

    testdir = Path(BASEPATH, 'common', 'testdir')
    # Test that testdir is created when it does not exist
    if testdir.exists():
        testdir.rmdir()
    makedirs(testdir)
    assert testdir.is_dir() is True

    # clean up
    notadir.unlink()
    testdir.rmdir()
