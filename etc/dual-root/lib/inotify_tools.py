# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
"""
Dual Root - Sync Inotify support tools

See class_inotify::Inotify
"""
# pylint: disable=
from collections.abc import (Callable)
from types import FrameType
import os
import signal
import subprocess
from subprocess import Popen


def _terminate_w_signals(pid: int):
    """ try sigterm then sigkill if needed """
    # if pid is not None:
    if pid > 1:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass


def terminate_one_inotify(pipe: Popen, pid: int):
    """
    When exiting, do what we can to shutdown all inotify processes.
    Possible pipe.terminate() may or may not be viable.
    """
    if pipe and pipe.poll() is None:
        try:
            pipe.terminate()
        except OSError:
            try:
                pipe.kill()
            except OSError:
                _terminate_w_signals(pid)
    else:
        _terminate_w_signals(pid)


def catch_signals(sig_handler: Callable[[int, FrameType | None], None]):
    """
    Catch and terminate
    """
    sigs = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP,
            signal.SIGQUIT, signal.SIGABRT,]

    for sig in sigs:
        signal.signal(sig, sig_handler)


def popen_one_inotify(watchdir: str) -> Popen | None:
    """
    Popen inotifywait in 'monitor' mode
     - return the pipe
     - use line buffering to ensure we avoid partial events coming back
    """
    # pylint: disable=R1732
    if not watchdir:
        print('inotify: No watch_dir given')
        return None

    cmd = ['/usr/bin/inotifywait']

    events = "attrib,create,move,modify,delete,unmount"
    opts = ['-m', '-r', '-e', events, '--format', '%e', watchdir]
    pargs = cmd + opts

    cmd_str = ' '.join(pargs)
    print(f'Starting {cmd_str}')

    pipe: Popen | None = None
    try:
        pipe = subprocess.Popen(pargs,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                text=True,
                                bufsize=1
                                )
    except OSError as err:
        pipe = None
        print(f'Failed to start inotify: {err}')

    return pipe
