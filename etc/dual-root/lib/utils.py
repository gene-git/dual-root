# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
  Dual Root Support Utils
  GC 2023
"""
from typing import (IO, Iterator, List, Tuple)
import os
import subprocess
from subprocess import SubprocessError


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


def run_prog(pargs,
             input_str: str = '',
             stdout: int = subprocess.PIPE,
             stderr: int = subprocess.PIPE) -> Tuple[int, str, str]:
    """
    run external program
    """
    if not pargs:
        return (0, '', 'Missing pargs')

    bstring: bytes | None = None
    if input_str:
        bstring = bytearray(input_str, 'utf-8')

    try:
        ret = subprocess.run(pargs, input=bstring, stdout=stdout,
                             stderr=stderr, check=False)

    except (FileNotFoundError, SubprocessError) as err:
        return (-1, '', str(err))

    retc = ret.returncode
    output = ''
    errors = ''

    if ret.stdout:
        output = str(ret.stdout, 'utf-8', errors='ignore')

    if ret.stderr:
        errors = str(ret.stderr, 'utf-8', errors='ignore')

    return (retc, output, errors)


def run_cmd(pargs: List[str]) -> List[str]:
    """
    Run cmd with provided arguments and return stdout.

    Variation of run_prog with simpler calling convention.
    Args:
        pargs (List[str]):
        Standard list of command and arguments.
    Returns:
        List[str]:
        List of lines of stdout from running program.
        May be empty list.

    """
    result: List[str] = []

    (ret, out, err) = run_prog(pargs)
    if ret != 0:
        if err:
            print(err)
        return result
    if out:
        result = out.splitlines()
    return result
