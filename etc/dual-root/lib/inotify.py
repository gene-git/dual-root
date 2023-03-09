# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Gene C
"""
 Dual Root - Sync Inotify support
"""
# pylint: disable=W0603
import os
import signal
import subprocess
from select import select

def terminate_one_inotify(pipe, pid):
    """
    Be nice if we exit and shutdown inotify
    If we got here pipe.terminate() may 
    not longer be useful
    """
    if pipe and pipe.poll() is None:
        try:
            pipe.terminate()
        except OSError:
            try:
                pipe.kill()
            except OSError:
                pass
    elif pid is not None:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

def catch_signals(sig_handler):
    """
    Catch and terminate
    """
    sigs = [signal.SIGINT,signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT, signal.SIGABRT,]
    for sig in sigs:
        signal.signal(sig, sig_handler)

def popen_one_inotify(watchdir):
    """
    open inotifywait in 'monitor' mode
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

    pipe = None
    try:
        pipe = subprocess.Popen(pargs, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                text=True, bufsize=1)
    except OSError as err:
        print(f'Failed to start inotify : {err}')

    return pipe

def inotify_event_handler(inotify):
    """
    Monitors all the inotify pipes and handles events on any of them.
     - on each event notify, run event_action for that item
     - each pipe.stdout is mapped back to watch item
    """
    watch_list = inotify.watch_list
    num_items = len(watch_list)

    if num_items < 1:
        print('Nothing to watch - event_handler quitting')
        return

    okay = True
    num_active = num_items

    while okay and num_active > 0 :

        #
        # Check which items are still active
        #
        read_list = []
        for item in watch_list:
            if item.pipe :
                if item.pipe.poll() is None:
                    read_list.append(item.pipe.stdout)
                else:
                    item.terminate()

        num_active = len(read_list)
        if num_active < 1:
            break

        try:
            (rdlist, _write, _err) = select(read_list, [],[])

            for stdout in rdlist:
                watch = inotify.stdout_map[stdout]
                event_line = stdout.readline()

                if 'unmount' in event_line:
                    print('Watch dir {watch.watch_dir} unmounted - terminating')
                    watch.pipe.terminate()
                    break

                #
                # Something changed - so lets sync.
                #
                watch.sync_item.sync()

        except OSError as err:
            print(f'Select err: {err}')
            okay = False
            break

    if not okay:
        inotify.terminate()
