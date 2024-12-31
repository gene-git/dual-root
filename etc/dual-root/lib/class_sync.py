# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  Dual Root Support 
  Simple class for handling sync (uses rsync)
"""
# pylint: disable=too-few-public-methods
import time
import threading
from .sync import sync_one
from .sync import check_sync_list
from .class_inotify import Inotify

class SyncItem:
    """
    One item to be watched and synced
     - Holds: source, destination_list, exclusion list 
     - standard rsync options are common and not per item
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # pylint: disable=too-many-instance-attributes
    def __init__(self, src, dst_list, excl_list, rsync_opts, delay, quiet, test):
        self.quiet = quiet
        self.test = test
        self.src = src
        self.dst_list = dst_list
        self.excl_list = excl_list
        self.rsync_opts = rsync_opts
        self.sync_delay = delay
        self.last_sync = None
        self.pending = False
        self.thread = None

    def sync(self):
        """
        sync myself
        """
        now = time.time()
        self.pending = True
        if (now - self.last_sync) > self.sync_delay:
            self.sync_one_thread(now=now)

    def sync_no_delay(self):
        """
        sync myself skip any delays
         - play nice with threads
        """
        self.pending = True
        self.sync_one_thread()

    def sync_one_thread(self, now=None):
        '''
        Run in thread
         - only run one at a time
        '''
        if not self.is_running():
            if now is None:
                now = time.time()
            self.last_sync = now
            self.pending = False
            args = (self, self.rsync_opts, self.quiet, self.test)
            self.thread = threading.Thread(target=sync_one, args=args)
            self.thread.start()

    def is_running(self):
        ''' check if have running sync thread '''
        if self.thread and self.thread.is_alive():
            return True
        return False

    def sync_if_needed(self, force=False):
        '''
        If have pending sync, then
         wait loop (30 sec sleeps) until existing sync completes then run again
        '''
        if self.pending or force:
            while self.is_running():
                time.sleep(30)
            self.sync_one_thread()

    def sync_pending(self, force=False):
        '''
        If have pending sync, then
         wait loop (30 sec sleeps) until existing sync completes then run again
        '''
        if self.pending or force:
            self.sync_one_thread()

class Sync:
    """
    little helper class for sync operations
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, sync_list, rsync_opts, delay, quiet, test):
        self.inotify = None
        self.sync_list = sync_list
        self.rsync_opts = rsync_opts
        self.sync_delay = delay if delay is not None else 300
        self.sync_items = []
        self.sync_delay = float(delay)

        self._items_from_list(quiet, test)

    def _items_from_list(self, quiet, test):
        """
        create list of SyncItems
        """
        delay = self.sync_delay
        if self.sync_list:
            for list_item in self.sync_list:
                src = list_item[0]
                dst_list = list_item[1]
                excl_list= []
                if len(list_item) > 2:
                    excl_list= list_item[2]
                sync_item = SyncItem(src, dst_list, excl_list, self.rsync_opts, delay, quiet, test)
                self.sync_items.append(sync_item)

    def check(self):
        """
        sanity checks on the list
        """
        return check_sync_list(self.sync_list)

    def sync_all_items(self):
        """
        sync all items
        """
        for item in self.sync_items:
            item.sync_if_needed(force=True)

    def sync_all_items_if_needed(self):
        """
        sync all items
        """
        for item in self.sync_items:
            item.sync_if_needed()

    def init_daemon(self):
        """
        Set up the daemon with inotify on all the items to be synced
        """
        self.inotify = Inotify()
        print('Sync Daemon: Adding items to watch list')
        for one_sync_item in self.sync_items:
            src = one_sync_item.src
            dst = one_sync_item.dst_list
            exc = one_sync_item.excl_list
            print(f'  [{src}, {dst}, {exc}')
            self.inotify.add_watch_item(one_sync_item)

        self.inotify.popen_inotify()
        print('Monitoring')
        self.inotify.event_handler()

        # Ensure any pending syncs are handled
        self.sync_all_items_if_needed()
