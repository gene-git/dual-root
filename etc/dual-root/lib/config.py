"""
Command line options
"""
# pylint: disable=too-many-instance-attributes, too-few-public-methods
from typing import (Any, List, Dict, Tuple)
import argparse

from ._read_config import read_config

type _Opt = Tuple[str | Tuple[str, str] | Tuple[str, str, str], Dict[str, Any]]
type SyncListElem = Tuple[str, List[str], List[str]]


def _avail_options(conf_file: str, efi_mount: str) -> List[_Opt]:
    """
    List of command line options for argparse
    """

    opts: List[_Opt] = []

    opts.append((('-b', '--bind'),
                 {'action': 'store_true',
                  'help': 'Bind mount active esp to efi mount'
                  }
                 ))

    opts.append((('-s', '--sync'),
                 {'action': 'store_true',
                  'help': 'Sync efi to alternate and any config sync dirs'
                  }
                 ))

    opts.append((('-sd', '--syncd'),
                 {'action': 'store_true',
                  'help': 'Start sync daemon which uses inotify'
                  }
                 ))

    opts.append((('-t', '--test'),
                 {'action': 'store_true',
                  'help': 'Test mode'
                  }
                 ))

    opts.append((('-q', '--quiet'),
                 {'action': 'store_true',
                  'help': 'Quiet mode'
                  }
                 ))

    opts.append((('-c', '--conf', '--config-file'),
                 {'default': conf_file,
                  'dest': 'config_file',
                  'help': f'Sync daemon config file ({conf_file})'
                  }))

    opts.append(('efi_mount',
                {'default': efi_mount,
                 'nargs': '?',
                 'help': f'Where to bind mount active esp ({efi_mount})'
                 }
                 ))

    return opts


class Config:
    """
    Config and command line options.
    """
    def __init__(self):
        """
        Parse command line to get config file.

        Read config. Command line overrides config file
        but in our case there is no overlap.

        Config defaults are in read_config()
        Command line option defaults are in parse_args()
        """
        #
        # config file
        #
        self.dualroot: bool = True
        self.rsync_opts: List[str] = []
        self.nice: int = 19
        self.ionice_class: int = 3  # 0=idle
        self.ionice_level: int = 6
        self.sync_delay: float = 300
        self.sync_list: List[SyncListElem] = []

        #
        # command line
        #
        self.bind: bool = False
        self.sync: bool = False
        self.syncd: bool = False
        self.test: bool = False
        self.quiet: bool = False
        self.config_file: str = ''
        self.efi_mount: str = ''

        parse_args(self)

        #
        # Now we know config filename, read it
        # and map to our attributes
        #
        config_dict = read_config(self.config_file)

        for (key, val) in config_dict.items():
            setattr(self, key, val)

        if self.syncd:
            self.sync = True


def parse_args(conf: Config):
    """
    Parse command line for any options.
    """
    desc = 'dual-root-tool : dual <esp> management tool'

    conf_file = '/etc/dual-root/sync-daemon.conf'
    efi_mount = '/boot'
    options = _avail_options(conf_file, efi_mount)

    par = argparse.ArgumentParser(description=desc)

    for opt in options:
        opt_list, kwargs = opt
        if isinstance(opt_list, str):
            par.add_argument(opt_list, **kwargs)
        else:
            par.add_argument(*opt_list, **kwargs)

    parsed = par.parse_args()
    if not parsed:
        return

    for (key, val) in vars(parsed).items():
        setattr(conf, key, val)
