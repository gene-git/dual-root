Changelog
=========

[2.9.0] ----- 2023-09-27
 * update project version  
 * Fixup Doc installer  
 * fix license install for new location  
 * Reorganize Docs and migrate to rst  
 * update CHANGELOG.md  

[2.8.0] ----- 2023-09-25
 * update project version  
 * sync code : remove obvious duplicate elements from rsync options list.  
 * We dont catch short vs long options or combined option flags such as "-t" vs "-atx"  
 * update CHANGELOG.md  

[2.7.0] ----- 2023-06-28
 * update project version  
 * update readme  
 * Sync once before starting the inotify based sync daemon  
 * Update README rsync_opts  
 * rsync options now adds --times --no-specials to rsync_opta  
 * update CHANGELOG.md  

[2.6.0] ----- 2023-06-27
 * update project version  
 * new rsync additional options  
 * default base options: "-axHAX --no-specials" which can be changed in the config file  
 * always added to base: "--atimes --open-noatime --exclude=/lost+found/ --delete""  
 * update CHANGELOG.md  

[2.5.0] ----- 2023-06-27
 * update project version  
 * Add rsync_opts to each sync_item  
 * typo fix  
 * Add new variable rsync_opts to config file.  
 * Defaults to "-axHAX --no-specials"  
 * update CHANGELOG.md  

[2.4.0] ----- 2023-06-26
 * update project version  
 * use --no-specials rsync option for the sync daemon  
 * More word smithing on readme  
 * update CHANGELOG.md  

[2.3.2] ----- 2023-06-26
 * update project version  
 * Minor readme tweak  
 * update CHANGELOG.md  

[2.3.1] ----- 2023-05-17
 * update project version  
 * Simplify Arch PKGBUILD and more closely follow arch guidelines  
 * update CHANGELOG.md  

[2.3.0] ----- 2023-04-29
 * update project version  
 * Fix typo made fixing previous typo ...  
 * update CHANGELOG.md  

[2.2.0] ----- 2023-04-29
 * update project version  
 * Fix typo in error message  
 * update CHANGELOG.md  

[2.1.1] ----- 2023-04-26
 * update project version  
 * For Arch mkpkg usersAdd _mkpkg_depends to to PKGBUILD to rebuild when python is updated  
 * Add short note about swap file for approach 1.  
 * update CHANGELOG.md  

[2.1.0] ----- 2023-03-12
 * update project version  
 * tidy inotify terminate()  
 * readme tweaks  
 * update CHANGELOG.md  

[2.0.3] ----- 2023-03-10
 * update project version  
 * More readme tweaks  
 * minor change to service unit description  
 * update CHANGELOG.md  

[2.0.2] ----- 2023-03-09
 * update project version  
 * Doc wordsmithing  
 * Wordsmithing README  
 * update CHANGELOG.md  

[2.0.1] ----- 2023-03-09
 * update project version  
 * Tidy some coding comments  
 * update CHANGELOG.md  

[2.0.0] ----- 2023-03-09
 * update project version  
 * update CHANGELOG.md  
 * update project version  
 * Tweak systemd service descriptions  
 * fix: add_dual_root needs emmpty exceptions list  
 * update README with new syncd info, fix buglet installing sample config  
 * debug off  
 * Now uses class Sync and class Inotify.  
 * Support for Approach 1 and Approach 2  
 * New optional sync-daemon.conf allows specifying what to sync with list of :  
 * [source, destination(s), exclusion(s)]  - each in rsync compatible form  
 * Complete rewrite of sync code - now in class Inotify  
 * Remove timeout=0 from select()  
 * update CHANGELOG.md  

[1.0.2] ----- 2023-03-07
 * update project version  
 * Remove inotify todo item - its done :)  
 * update CHANGELOG.md  

[1.0.1] ----- 2023-03-07
 * update project version  
 * fix comment  
 * Add comment on recovering from disk failure  
 * update CHANGELOG.md  

[1.0.0] ----- 2023-03-07
 * update project version  
 * update CHANGELOG.md  

[0.9.9] ----- 2023-03-07
 * update project version  
 * Edit dual-root-syncd.service desctiption  
 * Add missing [Install] in dual-root-syncd.service  
 * debug off  
 * Inotify sync option (dual-root-tool -sd) available  
 * dual-root-syncd.service to start the sync daemon  
 * update CHANGELOG.md  

[0.9.1] ----- 2023-03-07
 * update project version  
 * Message - use mountd "on"  
 * installer - duh  
 * installer typo with etc  
 * Refactor and tidy ups  
 * update CHANGELOG.md  

[0.9.0] ----- 2023-03-07
 * update project version  
 * Improve README  
 * fix installer path buglet  
 * tidy up installer  
 * Install uses /etc/dual-root  
 * update Install.rst instructions  
 * update CHANGELOG.md  

[0.8.0] ----- 2023-03-07
 * update project version  
 * Add -q quiet option  
 * small doc edits  
 * update CHANGELOG.md  

[0.7.0] ----- 2023-03-06
 * update project version  
 * missing install.rst in installer  
 * typo in installer script  
 * update CHANGELOG.md  

[0.6.0] ----- 2023-03-06
 * update project version  
 * update CHANGELOG.md  
 * update project version  
 * Add sphinx docs - cd docs; make latexpdf; make html  
 * add comment on avoiding mixing disk types  
 * update CHANGELOG.md  

[0.5.0] ----- 2023-03-06
 * update project version  
 * tweak doc  
 * More edits for dual-root-tool  
 * update CHANGELOG.md  

[0.4.0] ----- 2023-03-06
 * update project version  
 * add more protective checks  
 * update CHANGELOG.md  

[0.3.0] ----- 2023-03-06
 * update project version  
 * add sync and test mode  
 * update CHANGELOG.md  

[0.2.0] ----- 2023-03-06
 * update project version  
 * add packaging  
 * update CHANGELOG.md  

[0.1.0] ----- 2023-03-06
 * tool still sync but otherwise working okay - needs wider testing  
 * initial commit  

