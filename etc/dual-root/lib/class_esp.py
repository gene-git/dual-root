# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
 Dual Root Tool
  Identify which <esp> was used to boot the currently running system.

  - identify which <esp> was used to boot current system
  - support bind mounting this <esp> onto /boot
  - support rsyncing this onto the alternate <esp>

 Required
   python (> 3.9), efibootmgr, mount, rsync

Should a low level tool be in python? Probably not, but it
gets a working tool done reasonably safely and quickly.
This is far too complex for a bash script, but we
should probably make a statically linked C++ or C or rust
version at some point.

But for now this works.

 GC 2023
"""
# pylint: disable=too-few-public-methods
import os
from .utils import os_scandir
from .utils_block import device_to_uuid_mounts
from .utils_block import booted_esp_partuuid
from .utils_block import partuuid_to_device
from .utils_block import mount_to_uuid
from .utils_block import bind_mount
from .config import Config
from ._sync import Sync
from .prio import Prio


class Esp:
    """
    Details on one <esp>
    """
    # pylint: disable=

    def __init__(self):
        self.okay: bool = True
        self.partuuid: str = ''
        self.uuid: str = ''
        self.mount: str = ''
        self.mount_other: list[str] = []  # esp mounted other than /efiN
        self.dev: str = ''
        self.mount_list: list[str] = []

        self.uuid_and_mounts()

    def uuid_and_mounts(self):
        """
        For currently booted esp:
         - Get partuuid
         - Get uuid
        Use efibootmgr to identify booted esp
        """
        # pylint disable=

        self.partuuid = booted_esp_partuuid()
        self.dev = partuuid_to_device(self.partuuid)

        if not self.dev:
            print(f'Error finding device id of partuuid: {self.partuuid}')
            self.okay = False
            return

        #
        # Get UUID and all mounts of this UUID
        #
        (self.uuid, self.mount_list) = device_to_uuid_mounts(self.dev)

        #
        # Identify mount ~ /efiN
        #
        # self.mount_other = []
        for mount in self.mount_list:
            if len(mount) > 4 and mount[0:4] == '/efi':
                self.mount = mount
            else:
                self.mount_other.append(mount)


class EspInfo():
    """
    Identify esp info (UUID, mount points etc.

    Provide bind mounting current <esp> onto efi_mount (/boot)
    Provide rsync of current to alternate esp.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        #
        # esp is the currently booted esp.
        # Alternate esp's are listed in esp_alt
        #
        self.okay = True
        self.conf = Config()

        self.esp: Esp = Esp()
        self.esp_alt: list[Esp] = []

        self.efi_mount_uuid: str = ''
        self.efi_mounted: bool = False
        self.efi_uuid_correct: bool = False
        self.euid: int = os.geteuid()
        self.dual_root_mount_list: list[str] = []          # all /efi<n>
        self.dual_root_alt_mount_list: list[str] = []      # alternate /efi<n>
        self.is_dual_root: bool = False

        conf = self.conf
        self.sync_dual_root: bool = conf.dualroot

        prio = Prio(nice=conf.nice, ionice_class=conf.ionice_class,
                    ionice_level=conf.ionice_level)
        prio.set_prio()

        self.efi_mount_uuid = mount_to_uuid(conf.efi_mount)
        self.is_efi_mounted()
        self.dual_root_mounts()

        #
        # Install and check sync list
        #
        # sync_delay = config.get('sync_delay')
        # if sync_delay is None:
        #     sync_delay = 60

        self.sync = Sync(self.conf)
        if not self.sync.okay:
            self.okay = False

        #
        # if dual root syncing is True, then add to the sync list
        #
        self.add_dual_root_sync()

    def is_path_current_booted_esp(self, efi: str) -> bool:
        """
        Check if efi also the currently booted esp
        """
        if not efi:
            return False

        if self.esp.mount_list and efi in self.esp.mount_list:
            return True

        return False

    def is_efi_mounted(self):
        """
        Check if efi_mount (aka /boot) mounted and if UUID we want
        default efi_mount = '/boot'
        """
        self.efi_mounted = False
        self.efi_uuid_correct = False

        if self.conf.efi_mount in self.esp.mount_list:
            self.efi_mounted = True
            if self.efi_mount_uuid == self.esp.uuid:
                self.efi_uuid_correct = True

    def print_info(self):
        """ print useful info """
        if not self.conf.quiet:
            txt = f'{self.esp.mount_list} : {self.esp.uuid}'
            print(f'Booted esp: {self.esp.dev} : {txt}')

    def bind_mount_efi(self):
        """
        Bind mount current <esp> from esp.mount onto efi_mount (/boot)
            esp_mount typically /efi0 or /efi
            efi_mount typically /boot
            check that efi_mount (/boot) is not mounted already
        """
        conf = self.conf
        if self.efi_mounted:
            if self.efi_uuid_correct:
                txt = f'{self.esp.mount} already mounted on {conf.efi_mount}'
                print(f'{self.esp.uuid}: {txt}')
            else:
                txt = 'fmounted but uuid wrong - should be {self.esp.uuid}'
                print(f'{conf.efi_mount}: {txt}')
        elif not self.esp.mount:
            txt = 'bind mount skipped: esp not mounted on /efi0,/efi1 ...'
            print('Not dual root: {txt}')
        else:
            print(f'mount --bind {self.esp.mount} {conf.efi_mount}')
            if self.euid == 0 and not conf.test:
                bind_mount(self.esp.mount, conf.efi_mount)
            else:
                print('Must be non-test mode and root to use bind mount')

    def dual_root_mounts(self):
        """
        Make a list of all the mounts names /efi<N>
         - Should we exclude booted /efi<n>
        """
        self.dual_root_mount_list = []
        self.dual_root_alt_mount_list = []

        root_scan = os_scandir('/')
        if not root_scan:
            return

        for item in root_scan:
            path = item.path
            if path.startswith('/efi') and len(path) > 4:
                self.dual_root_mount_list.append(path)
                if not self.is_path_current_booted_esp(path):
                    self.dual_root_alt_mount_list.append(path)

        if len(self.dual_root_mount_list) > 1:
            self.is_dual_root = True

    def add_dual_root_sync(self):
        """
        If syn'cing dual root add to the sync list
          - source is currently booted efi mount
          - dest is list of alternates
        """
        if not self.sync_dual_root:
            return

        current_efi = self.esp.mount
        all_dual_mounts = self.dual_root_mount_list
        alt_dual_mounts = self.dual_root_alt_mount_list

        if not self.is_dual_root or not all_dual_mounts:
            txt = '(2 or more /efi<n> not found) -  nothing to sync'
            print('Not dual root: {txt}')
            return

        if len(all_dual_mounts) == 1:
            this_efi = all_dual_mounts[0]
            txt = f'({this_efi}) -  nothing to sync'
            print(f'Only 1 dual root esp found: {txt}')
            return

        if len(alt_dual_mounts) == 0:
            print('No alternate dual root esp found -  nothing to sync')
            return

        #
        # Add trailing "/" - want to rsync /efi0/ /efi1
        #
        dest_list = []
        for dest in self.dual_root_alt_mount_list:
            dest_list.append(f'{dest}/')

        exclusions: list[str] = []
        sync_item = (f'{current_efi}/', dest_list, exclusions)
        self.sync.add_sync_list_items(self.conf, [sync_item])

    def sync_all_items(self):
        """
        One shot sync - no daemon
        """
        self.sync.sync_all_items()

    def sync_daemon_start(self):
        """
        Sunc Daemon:
         - Use inotify to monitor current efi and sync
           alternates whenever change detected
        """
        self.sync.init_daemon()
