# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
  Dual Root Support Utils
  GC 2023
"""
from typing import (IO)
from collections.abc import Iterator
import os
import subprocess
from subprocess import SubprocessError

from .run_prog import run_prog


def os_scandir(tdir: str) -> Iterator[os.DirEntry] | None:
    """
    Scandir with exception handling
    """
    scan: Iterator[os.DirEntry] | None = None

    if os.path.exists(tdir) and os.path.isdir(tdir):
        try:
            scan = os.scandir(tdir)
        except OSError as _error:
            scan = None
    return scan


def open_file(path: str, mode: str) -> IO | None:
    """
    Open a file and return file object
    """
    # pylint: disable=unspecified-encoding,consider-using-with
    try:
        fobj = open(path, mode)
    except OSError as err:
        print(f'Error opening file {path}: {err}')
        fobj = None
    return fobj


def run_cmd(pargs: list[str]) -> list[str]:
    """
    Run cmd with provided arguments and return stdout.

    Variation of run_prog with simpler calling convention.
    Args:
        pargs (list[str]):
        Standard list of command and arguments.
    Returns:
        list[str]:
        list of lines of stdout from running program.
        May be empty list.

    """
    result: list[str] = []

    (ret, out, err) = run_prog(pargs)
    if ret != 0:
        if err:
            print(err)
        return result
    if out:
        result = out.splitlines()
    return result
