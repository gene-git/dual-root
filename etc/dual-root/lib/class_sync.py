# SPDX-License-Identifier: MIT
# Copyright (c) 2023, Gene C
"""
  Dual Root Support 
  Simple class for handling sync (uses rsync)
"""
from .sync import sync_one
from .sync import check_sync_list
from .class_inotify import Inotify

class SyncItem:
    """
    One item to be watched and synced
     - Holds: source, destination_list, exclusion list 
     - standard rsync options are common and not per item
    """
    # pylint: disable=R0903
    def __init__(self, src, dst_list, excl_list, rsync_opts, quiet, test):
        self.quiet = quiet
        self.test = test
        self.src = src
        self.dst_list = dst_list
        self.excl_list = excl_list
        self.rsync_opts = rsync_opts

    def sync(self):
        """
        sync myself
        """
        sync_one(self, self.rsync_opts, self.quiet, self.test)

class Sync:
    """
    little helper class for sync operations
    """
    def __init__(self, sync_list, rsync_opts, quiet, test):
        self.inotify = None
        self.sync_list = sync_list
        self.rsync_opts = rsync_opts
        self.sync_items = []
        self._items_from_list(quiet, test)

    def _items_from_list(self, quiet, test):
        """
        create list of SyncItems
        """
        if self.sync_list:
            for list_item in self.sync_list:
                src = list_item[0]
                dst_list = list_item[1]
                excl_list= []
                if len(list_item) > 2:
                    excl_list= list_item[2]
                sync_item = SyncItem(src, dst_list, excl_list, self.rsync_opts, quiet, test)
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
            item.sync()

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
