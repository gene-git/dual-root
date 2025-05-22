# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  Dual Root Support
  Simple class for handling sync (uses rsync)
"""
# pylint: disable=too-few-public-methods
import threading


class RsyncItem:
    """
    Arguments (src, dst, excl) for one rsync

    Args:
        src (str):
            source to be copies

        dst (str | list[str]):
            Destination - can be list.

        excl (list[str]):
            list of exclusions not to copy

        rsync_opts (str):
            Options to use with rsync.
    """
    def __init__(self,
                 src: str,
                 dst: str | list[str],
                 excl: list[str],
                 rsync_opts: list[str]
                 ):
        self.src: str = src
        self.dst: str | list[str] = dst
        self.rsync_opts: list[str] = rsync_opts
        self.excl: list[str] = excl


class SyncItemBase:
    """
    One item to be watched and synced
     - Holds: source, destination_list, exclusion list
     - standard rsync options are common and not per item
    """
    # pylint: disable=
    # pylint: disable=
    def __init__(self,
                 rsync_item: RsyncItem,
                 delay: float,
                 quiet: bool,
                 test: bool
                 ):
        self.quiet = quiet
        self.test = test

        self.rsync_item: RsyncItem = rsync_item
        self.sync_delay: float = delay
        self.last_sync: int = -1
        self.pending: bool = False
        self.thread: threading.Thread | None = None
