# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  Dual Root Support
  Simple class for handling sync (uses rsync)
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments, too-many-positional-arguments
from typing import (List)
from .sync import (rsync_options_final, check_sync_list)
from .class_inotify import Inotify
from ._syncitem_base import (RsyncItem)
from ._syncitem import (SyncItem)
from ._types import (SyncListElem)
from .config import Config


class Sync:
    """
    little helper class for sync operations
    """
    #         sync_list: List[SyncListElem],
    #         rsync_opts: List[str],
    #         delay: float = 300,
    #         quiet: bool = False,
    #         test: bool = False):
    def __init__(self, conf: Config):
        """
        Args:
            sync_list (List[src: str, dst: str or List[str], excl: List[str]]):
        """
        self.okay: bool = True
        self.inotify: Inotify
        # self.sync_list: List[SyncListElem] = sync_list
        self.sync_delay = conf.sync_delay

        #
        # check sync list
        #
        if not check_sync_list(conf.sync_list):
            self.okay = False
            return

        #
        # map sync list to sync_items
        #
        self.sync_items: List[SyncItem] = []
        self.rsync_opts = rsync_options_final(conf.rsync_opts,
                                              test=conf.test)

        self.sync_items = self._sync_list_to_items(conf, conf.sync_list)

    def _sync_list_to_items(self,
                            conf: Config,
                            sync_list: List[SyncListElem]) -> List[SyncItem]:
        """
        create the list of SyncItems from input sync_list
        """
        quiet = conf.quiet
        test = conf.test

        sync_items: List[SyncItem] = []

        if not sync_list:
            return sync_items

        for list_item in sync_list:
            src = list_item[0]
            dst = list_item[1]

            excl: List[str] = []
            if len(list_item) > 2:
                excl = list_item[2]

            rsync_item = RsyncItem(src, dst, excl, self.rsync_opts)
            sync_item = SyncItem(rsync_item, self.sync_delay,
                                 quiet, test)
            sync_items.append(sync_item)

        return sync_items

    def add_sync_list_items(self, conf: Config, sync_list: List[SyncListElem]):
        """
        Adds sync_items from sync list items.

        Appends to existing list.  """
        self.sync_items += self._sync_list_to_items(conf, sync_list)

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
            src = one_sync_item.rsync_item.src
            dst = one_sync_item.rsync_item.dst
            exc = one_sync_item.rsync_item.excl
            print(f'  ({src}, {dst}, {exc})')
            self.inotify.add_watch_item(one_sync_item)

        self.inotify.popen_inotify()
        print('Monitoring')
        self.inotify.event_handler()

        # Ensure any pending syncs are handled
        self.sync_all_items_if_needed()
