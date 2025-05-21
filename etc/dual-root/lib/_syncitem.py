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
from ._syncitem_base import (SyncItemBase)


class SyncItem(SyncItemBase):
    """
    One item to be watched and synced
     - Holds: source, destination_list, exclusion list
     - standard rsync options are common and not per item
    """
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
            args = (self, self.quiet)
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
