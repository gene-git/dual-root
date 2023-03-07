# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Gene C
"""
 Dual Root - Sync Inotify support
"""
# pylint: disable=W0603
import os
import sys
import signal
import subprocess
import atexit
from select import select

#
# Make sure we kill inotify properly on exit
#
Inotify_Pipe = None
Inotify_Pid = None

def _terminiate_inotify():
    """
    Be nice if we exit and shutdown inotify
    If we got here pipe.terminate() may 
    not longer be useful
    """
    if Inotify_Pipe and Inotify_Pipe.poll() is None:
        try:
            Inotify_Pipe.terminate()
        except OSError:
            try:
                Inotify_Pipe.kill()
            except OSError:
                pass
    elif Inotify_Pid is not None:
        try:
            os.kill(Inotify_Pid, signal.SIGTERM)
        except OSError:
            try:
                os.kill(Inotify_Pid, signal.SIGKILL)
            except OSError:
                pass

def _signal_handler(signum, _frame):
    """
    Ensure clean shutdown when using inotify
    """
    print(f'Signal caught {signum}- exiting')
    _terminiate_inotify()
    sys.exit(0)


def _popen_inotify(watchdir):
    """
    open inotifywait in 'monitor' mode
     - return the pipe
     - use line buffering to ensure we avoid partial events coming back
    """
    # pylint: disable=R1732
    global Inotify_Pipe
    global Inotify_Pid

    if not watchdir:
        print('No watch dir given for inotify')
        return

    cmd = ['/usr/bin/inotifywait']
    events = "attrib,create,move,modify,delete,unmount"
    opts = ['-m', '-r', '-e', events, '--format', '%e', watchdir]
    pargs = cmd + opts

    cmd_str = ' '.join(pargs)
    print(f'Starting {cmd_str}')
    pipe = None

    try:
        pipe = subprocess.Popen(pargs, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                text=True, bufsize=1)
        if pipe:
            Inotify_Pipe = pipe
            Inotify_Pid = pipe.pid

    except OSError as err:
        print(f'Failed to start inotify : {err}')

    return pipe

def _inotify_event_handler(espinfo, pipe):
    """
    Monitors the inotify output 
     - on event notifiy, run one time sync using espinfo.sync_alt_efi()
    """
    global Inotify_Pipe
    if pipe is None:
        print('No inotify pipe - event_handler quitting')
        return

    timeout = 0
    all_okay = True
    while all_okay and pipe.poll() is None:
        try:
            (_stdout, _write, _err) = select([pipe.stdout], [],[], timeout)

            event_line = pipe.stdout.readline()

            if 'unmount' in event_line:
                print('Inofify dir unmounted - terminating')
                pipe.terminate()
                all_okay = False
                break

            #
            # Change - so lets sync.
            #
            espinfo.sync_alt_efi()

        except OSError as err:
            print(f'Select err: {err}')
            all_okay = False
            break

    if not all_okay:
        if pipe.poll() is not None:
            Inotify_Pipe = None
        #
        # May be over"kill" -  be sure inotify is shutdown
        #
        _terminiate_inotify()


def popen_inotify_daemon(espinfo, watchdir):
    """
    initialize:
     - catch signals
     - clean up on exit
    """
    #
    # Set up
    #
    sigs = [signal.SIGINT,signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT, signal.SIGABRT,]
    for sig in sigs:
        signal.signal(sig, _signal_handler)

    atexit.register(_terminiate_inotify)

    #
    # monitor current efi for changes
    #
    pipe = _popen_inotify(watchdir)
    if not pipe:
        print('Failed to start inotify watch')
        return
    _inotify_event_handler(espinfo, pipe)
