# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
 Dual Root - Inotify Class
"""
# pylint: disable=global-statement
from typing import (Dict, List)
from types import FrameType
import atexit
from select import select
from subprocess import Popen

from .inotify_tools import (catch_signals, terminate_one_inotify)
from .inotify_tools import popen_one_inotify

from ._syncitem import SyncItem


class WatchItem:
    """ one watched directory """
    def __init__(self, sync_item: SyncItem):
        """
        One inotify item
         - On event the action taken is calling: self.sync_item.sync()
        """
        self.sync_item: SyncItem = sync_item
        self.pipe: Popen | None = None
        self.pid: int = -1

    def terminate(self):
        """
        Ensure child inotify process is temrminated
        """
        if self.pipe is not None:
            terminate_one_inotify(self.pipe, self.pid)
        self.pipe = None
        self.pid = -1

    def popen_inotify(self):
        """
        Open up pipe to inotify process
        """
        watched = self.sync_item.rsync_item.src
        self.pipe = popen_one_inotify(watched)

        if self.pipe:
            self.pid = self.pipe.pid
        else:
            print(f'Warning: inotify on {watched} failed')


WatchList: List[WatchItem] = []


def inotify_signal_handler(_sig_num: int, _sig_frame: FrameType | None):
    """
    Clean up
    """
    for item in WatchList:
        item.terminate()


class Inotify:
    """
    Handle Multiple Inotify Change Events
     - Call add_watch_item() for each being watched
     - popen_inotify() to open one pipe to each monitor
     - event_handler()

    For simplicity we use "/usr/bin/inotifywait".
    """
    def __init__(self):
        """
        Add all the watch points then init()
         - Map each items pipe.stdout -> item, when selec() can recover item.

         stdout_map maps(pipe.stdout -> watch item)
        """
        global WatchList
        self.watch_list: List[WatchItem] = []
        self.stdout_map: Dict[int, WatchItem] = {}

        WatchList = self.watch_list
        catch_signals(inotify_signal_handler)
        atexit.register(self.terminate)

    def add_watch_item(self, sync_item: SyncItem):
        """
        Add this to the watch list
         - make sure no existing match or reverse match.
        """
        watch = WatchItem(sync_item)
        self.watch_list.append(watch)

    def terminate(self):
        """
        Be sure all inotify processes are properly terminated
        """
        for item in self.watch_list:
            item.terminate()

    def popen_inotify(self):
        """
        Open pipes to each inotify item
        """
        for item in self.watch_list:
            item.popen_inotify()
            if item.pipe and item.pipe.stdout:
                map_key = item.pipe.stdout.fileno()
                self.stdout_map[map_key] = item

    def event_handler(self):
        """
        Wait and handle any events
        """
        _inotify_event_handler(self)


def _inotify_event_handler(inotify: Inotify):
    """
    Monitors all inotify pipes and handles events on any of them.
     - on each event notify, run the correponding item's sync() function
     - Use pipe.stdout map to find associated sync_item from the file IO
       returned by select()
    """
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    watch_list = inotify.watch_list
    num_items = len(watch_list)

    if num_items < 1:
        print('Nothing to watch - event_handler quitting')
        return

    okay = True
    num_active = num_items

    while okay and num_active > 0:
        #
        # Check which items are still active
        #
        read_list = []
        for item in watch_list:
            if item.pipe:
                if item.pipe.poll() is None:
                    read_list.append(item.pipe.stdout)
                else:
                    item.terminate()

        num_active = len(read_list)
        if num_active < 1:
            break

        # Since rsync is run in own thread - there can be pending
        # items in queue;  so we periodically (every 15 mins) request
        # any pending sync get run
        timeout = 15*60
        try:
            (rdlist, _write, _err) = select(read_list, [], [], timeout)

            if not rdlist:
                # on timeout sync any pending items
                for item in watch_list:
                    item.sync_item.sync_pending()

            for stdout in rdlist:
                map_index = stdout.fileno()
                watch = inotify.stdout_map[map_index]
                event_line = stdout.readline()

                if 'unmount' in event_line:
                    txt = 'unmounted - terminating'
                    print(f'Watch dir {watch.sync_item.rsync_item.src} {txt}')
                    if watch.pipe is not None:
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
