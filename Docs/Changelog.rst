=========
Changelog
=========

Tags
====

::

	0.2.0 (2023-03-06) -> 3.2.0 (2025-05-20)
	73 commits.

Commits
=======


* 2025-05-20  : **3.2.0**

::

                Code improvements:
                  PEP-8, PEP-257, PEP-484 PEP-561
                  Simplify, Refactor code and rename when it helps clarity.
 2024-12-31     update Docs/Changelog Docs/dual-root.pdf

* 2024-12-31  : **3.1.1**

::

                Add git key to Arch Package and fix typo in PKGBUILD
                update Docs/Changelog Docs/dual-root.pdf

* 2024-12-31  : **3.1.0**

::

                more spdx tags
 2024-10-17     update Docs/Changelog Docs/dual-root.pdf

* 2024-10-17  : **3.0.0**

::

                Performance improvements:
                 - sync daemon now defaults to running with: nice=15, ionice_class=IDLE
                 - Inotify triggers now placed on sync queue which is run in separate thread
                 and queue run must wait sync
                   delay seconds before being run again. Each dir monitored by inotify has
                   its own queue.
                 - Periodic queue check/flushes are also run every 15 mins - this is also
                 run on exit to
                   ensure all pending syncs are completed.
                 - New variables in sync daemon config are available
                   nice, ionice_class and ionice_value; see man ioprio_set
                   defaults: nice=15, ionice_class=3 (IDLE)
                   sync_delay = 300 which is the minimum time between queue runs
 2023-09-27     update Docs/Changelog.rst

* 2023-09-27  : **2.9.0**

::

                Reorganize Docs and migrate to rst
 2023-09-25     update CHANGELOG.md

* 2023-09-25  : **2.8.0**

::

                sync code : remove obvious duplicate elements from rsync options list.
                  We dont catch short vs long options or combined option flags such as "-t"
                  vs "-atx"
 2023-06-28     update CHANGELOG.md

* 2023-06-28  : **2.7.0**

::

                rsync options now adds --times --no-specials to rsync_opta
                Sync once before starting the inotify based sync daemon
                update README
 2023-06-27     update CHANGELOG.md

* 2023-06-27  : **2.6.0**

::

                new rsync additional options
                        default base options: "-axHAX --no-specials" which can be changed in
                        the config file
                        always added to base: "--atimes --open-noatime
                        --exclude=/lost+found/ --delete""
                update CHANGELOG.md

* 2023-06-27  : **2.5.0**

::

                Add new variable rsync_opts to config file.
                  Defaults to "-axHAX --no-specials".
 2023-06-26     update CHANGELOG.md

* 2023-06-26  : **2.4.0**

::

                use --no-specials rsync option for the sync daemon
                More word smithing on readme
                update CHANGELOG.md

* 2023-06-26  : **2.3.2**

::

                minor readme tweak
 2023-05-17     update CHANGELOG.md

* 2023-05-17  : **2.3.1**

::

                Simplify Arch PKGBUILD and more closely follow arch guidelines
 2023-04-29     update CHANGELOG.md

* 2023-04-29  : **2.3.0**

::

                Fix typo when fixing previous typo ...
                update CHANGELOG.md

* 2023-04-29  : **2.2.0**

::

                Fix typo in error message
 2023-04-26     update CHANGELOG.md

* 2023-04-26  : **2.1.1**

::

                For Arch mkpkg users Add _mkpkg_depends to PKGBUILD so rebuilds package when
                python is updated
 2023-03-12     Add short note about swap file for approach 1.
                update CHANGELOG.md

* 2023-03-12  : **2.1.0**

::

                tidy / simplify inotify terminate() method.
                readme tweaks
 2023-03-10     update CHANGELOG.md

* 2023-03-10  : **2.0.3**

::

                Readme tweaks, systemd unit description improvements
 2023-03-09     update CHANGELOG.md

* 2023-03-09  : **2.0.2**

::

                Doc wordsmithing
                Wordsmithing README
                update CHANGELOG.md

* 2023-03-09  : **2.0.1**

::

                Tidy some coding comments
                update CHANGELOG.md

* 2023-03-09  : **2.0.0**

::

                Tweak systemd service descriptions
                update README with new syncd info
                Re-write sync code
                  New Sync and Inotify classes
                New optional sync-daemon.conf allows specifying what to sync with list of :
                    [source, destination(s), exclusion(s)]  - each in rsync compatible form
                Can be used with Approach 2
                Remove timeout=0 from select()
 2023-03-07     update CHANGELOG.md

* 2023-03-07  : **1.0.2**

::

                Forgot to add dual-root-syncd.service file - added
                Remove inotify todo item - its done :)
                update CHANGELOG.md

* 2023-03-07  : **1.0.1**

::

                Comment change in inotify code. Add couple lines on recovering from disk
                failure to docs
                Add comment on recovering from disk failure
                update CHANGELOG.md

* 2023-03-07  : **1.0.0**

::

                Release 1.0.0
                Inotify sync option (dual-root-tool -sd) available
                dual-root-syncd.service to start the sync daemon
                update CHANGELOG.md

* 2023-03-07  : **0.9.1**

::

                update to 0.9.1
                Refactor and tidy up code
                update CHANGELOG.md

* 2023-03-07  : **0.9.0**

::

                Add -q quiet option to dual-root-tool
                update Install.rst instructions
                Install uses /etc/dual-root
                tidy up installer
 2023-03-06     small doc edits
                update CHANGELOG.md

* 2023-03-06  : **0.7.0**

::

                fix installer typo
                update CHANGELOG.md

* 2023-03-06  : **0.6.0**

::

                Add sphinx docs - cd docs; make latexpdf; make html
                update CHANGELOG.md

* 2023-03-06  : **0.5.0**

::

                tweak doc, update to 0.5.0
                More edits for dual-root-tool
                update CHANGELOG.md

* 2023-03-06  : **0.4.0**

::

                add more protective checks
                update CHANGELOG.md

* 2023-03-06  : **0.3.0**

::

                Add sync and test mode
                update CHANGELOG.md

* 2023-03-06  : **0.2.0**

::

                Add dual-root-tool and bind service
                more doc updates
                Initial commit


