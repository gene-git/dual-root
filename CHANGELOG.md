# Changelog

## [2.0.2] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-09
 - Doc wordsmithing  
 - Wordsmithing README  
 - update CHANGELOG.md  

## [2.0.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-09
 - Tidy some coding comments  
 - update CHANGELOG.md  

## [2.0.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-09
 - Tweak systemd service descriptions  
   update README with new syncd info  
   Re-write sync code  
   New Sync and Inotify classes  
   New optional sync-daemon.conf allows specifying what to sync with list of :  
   [source, destination(s), exclusion(s)]  - each in rsync compatible form  
   Can be used with Approach 2  
   Remove timeout=0 from select()  
 - update CHANGELOG.md  

## [1.0.2] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-07
 - Forgot to add dual-root-syncd.service file - added  
 - Remove inotify todo item - its done :)  
 - update CHANGELOG.md  

## [1.0.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-07
 - Comment change in inotify code. Add couple lines on recovering from disk failure to docs  
 - Add comment on recovering from disk failure  
 - update CHANGELOG.md  

## [1.0.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-07
 - Release 1.0.0  
 - Inotify sync option (dual-root-tool -sd) available  
   dual-root-syncd.service to start the sync daemon  
 - update CHANGELOG.md  

## [0.9.1] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-07
 - update to 0.9.1  
 - Refactor and tidy up code  
 - update CHANGELOG.md  

## [0.9.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-07
 - Add -q quiet option to dual-root-tool  
   update Install.rst instructions  
   Install uses /etc/dual-root  
   tidy up installer  
 - small doc edits  
 - update CHANGELOG.md  

## [0.7.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-06
 - fix installer typo  
 - update CHANGELOG.md  

## [0.6.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-06
 - Add sphinx docs - cd docs; make latexpdf; make html  
 - update CHANGELOG.md  

## [0.5.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-06
 - tweak doc, update to 0.5.0  
 - More edits for dual-root-tool  
 - update CHANGELOG.md  

## [0.4.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-06
 - add more protective checks  
 - update CHANGELOG.md  

## [0.3.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-06
 - Add sync and test mode  
 - update CHANGELOG.md  

## [0.2.0] ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2023-03-06
 - Add dual-root-tool and bind service  
 - more doc updates  
 - Initial commit  

