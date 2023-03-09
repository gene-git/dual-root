# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Gene C
"""
 Dual Root - Inotify Class
"""
import atexit

from .inotify import terminate_one_inotify
from .inotify import catch_signals
from .inotify import inotify_event_handler
from .inotify import popen_one_inotify

class WatchItem:
    """ one watched directory """
    def __init__(self, sync_item):
        """
        One inotify item
         - action will be called : action(watch_dir, dest_dir_list)
        """
        self.sync_item = sync_item
        self.pipe = None
        self.pid = None

    def terminate(self):
        """
        Ensure child inotify process is temrminated
        """
        if self.pipe or self.pid:
            self.pipe.terminate()
            if self.pipe.poll() is not None:
                # didn't end so kill it
                terminate_one_inotify(self.pipe, self.pid)
        self.pipe = None
        self.pid = None

    def popen_inotify(self):
        """
        Open up pipe to inotify process
        """
        watched = self.sync_item.src
        self.pipe = popen_one_inotify(watched)
        if self.pipe:
            self.pid = self.pipe.pid
        else:
            print(f'Warning: inotify on {watched} failed')

WatchList = []
def inotify_signal_handler(_sig_num, _sig_frame):
    """
    Clean up
    """
    # pylint: disable=R1732
    for item in WatchList:
        item.terminate()

class Inotify:
    """
    Handle Multiple Inotify Change Events
    To register watchdir called provides watch elem:
     - watchdir, destdir_list, action_function
       action_function(watch_dir, destdir_list)
    """
    def __init__(self):
        """
        Handle list of items
        Add all the watch points then init()
         - Map each items pipe.stdout -> item, when selec() can recover item.
        """
        # pylint: disable=W0603
        global WatchList
        self.watch_list = []            # list of watch items
        self.stdout_map = {}            # map pipe.stdout -> item

        WatchList = self.watch_list
        catch_signals(inotify_signal_handler)
        atexit.register(self.terminate)

    def add_watch_item(self, sync_item):
        """
        Add this to the watch list
         - make sure no existing match or reverse match.
        """
        watch = WatchItem(sync_item)
        self.watch_list.append(watch)

    def terminate(self):
        """
        Make sure all the inotify processes are properl terminated
        """
        for item in self.watch_list:
            item.terminate()

    def popen_inotify(self):
        """
        Open pipes to each inotify item
        """
        for item in self.watch_list:
            item.popen_inotify()
            if item.pipe:
                self.stdout_map[item.pipe.stdout] = item

    def event_handler(self):
        """
        Wait and handle any events
        """
        inotify_event_handler(self)
