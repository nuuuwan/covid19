# covid19

## Setup and Install

```
pip install covid19-nuuuwan
```
* See https://nuwans.medium.com/analyzing-covid19-in-sri-lanka-with-python-caea03296381 for some examples

## Release History

* [2021-08-18 09:05AM] run-2021-08-18
  * Updated README
  * Added checks for Mullaitivu and Mannar
  * Pre-Merge
* [2021-08-18 09:36AM] Update GoogleMaps Link
  * Updated README
  * Pre-Merge
* [2021-08-18 04:11PM] Optimize lk-vax-center
  * Updated README
  * Added get_vax_centers
  * Added get_vax_center_index (untested); lang improvements
  * Pre-Merge
* [2021-08-18 04:52PM] remove accidential files
  * Updated README
  * Done
  * Pre-Merge
* [2021-08-18 04:55PM] lk-vax-center fixes
  * Updated README
  * Pre-Merge
  * Pre-Merge
  * Added TODO.md
* [2021-08-19 08:31AM] Save PDF with Data ID
  * Updated README
  * Pre-Merge
* [2021-08-19 08:44AM] Update Folder Structure
  * Updated README
  * Pre-Merge
* [2021-08-19 08:45AM] Split lk-vax-center pipeline
  * Updated README
  * Added files
  * scrape_google_id.py complete
  * scrape_pdf Done
  * parse_pdf.py Done
  * expand.py done
  * summarise.py done
  * finalize.py done
  * Pre-Merge
  * Updated TODO
* [2021-08-19 10:07AM] Add District IDs
  * Updated README
  * Pre-Merge
* [2021-08-19 10:08AM] lk-vax-centers: Add Meta Data
  * Updated README
  * Added metadata to pipe
  * Added get_metadata_index
  * expand uses metadata
  * expand uses metadata
  * expand complete
  * Done
  * Pre-Merge
  * Removed logging
  * Bug in workflow
  * Add new metadata
  * Added district data
* [2021-08-19 11:26AM] lk-vax-centers Expand Data
  * Updated README
  * Pre-Merge
* [2021-08-20 06:58AM] Clean Addresses
  * Updated README
  * metadata_validate complete
  * Pre-Merge
* [2021-08-20 08:02AM] VaxCenters Clean Addresses 2
  * Updated README
  * Pre-Merge
  * #AddressBugs Kothmale
  * #AddressBugs Kothmale
  * #AddressBugs Kothmale-2
  * Minor
  * #AddrBugs Elpitiya, Bibila
  * #AddrBug Kalutara South
  * #AddrBug Weligama
  * #AddrBug Kaluwanchikudy Kokkadichcholai
  * metadata fixes
  * Done
* [2021-08-20 08:58AM] Normalize Meta Data First
  * Updated README
  * Added find_metadata
  * Removed accidental files
  * Pre-Merge
  * Merged
  * Minor: metadata_validate.py
* [2021-08-20 10:16AM] metadata_validate.py updates
  * Updated README
  * Added examples stdev=2
  * Pre-Merge
  * Re-added police station
  * Readded police stations
  * Update README
* [2021-08-20 01:24PM] lk-vax-centers Split Translation and Geo
  * Updated README
  * Parse1
  * Parse1
  * Added CACHE_DIR
  * Done
  * removed metadata
  * Pre-Merge
* [2021-08-20 02:35PM] Rationalize Data
  * Updated README
  * Added district/police
  * Test i18n
  * Pre-Merge
  * Tested new pipeline
* [2021-08-20 06:11PM] lk-vax-centers Opt.
  * Updated README
  * Pre-Merge
* [2021-08-20 06:11PM] lk-vax-centers Opt
  * Updated README
  * expand_i18n test
  * expand_i18n tested
  * Done
  * Pre-Merge
  * Removed accid
* [2021-08-20 08:13PM] scrape_vax_schedule.py
  * Updated README
  * Added scrape_tentative_vax_schedule
  * Done
  * Pre-Merge
  * Done validating 2021-08-21
  * Added Kalutara and Kaduwela Police
  * Updated get_correct_district
* [2021-08-23 09:54AM] 2021-08-23 Corrections
  * Updated README
  * Pre-Merge
  * Removed acc.
* [2021-08-24 07:33AM] 2021-08-24 Corrections
  * Updated README
  * Done
  * Pre-Merge
* [2021-08-25 07:30AM] 2021-08-25 Corrections
  * Updated README
  * Pre-Merge
* [2021-08-26 07:23AM] Add Moderna Dose 2
  * Updated README
  * New Folders
  * Fixed
  * Pre-Merge
* [2021-08-26 07:35AM] LK Vax Centers - Split Download and Upload
  * Updated README
  * Done
  * Pre-Merge
* [2021-08-26 07:41AM] Shift Pipelines to Production
  * Updated README
  * Updated Upload
  * Updated Download
  * Pre-Merge
* [2021-08-26 07:44AM] 2021-08-26 Corrections
  * Updated README
  * Updated POLICE_INDEX
  * Pre-Merge
  * Updated local workflows
  * Speedup vax-center pipeline start
  * Permissions
* [2021-08-26 08:36AM] Speedup vax-center pipeline
  * Updated README
  * Done
  * Pre-Merge
* [2021-08-26 08:43AM] Location Corrections
  * Updated README
  * Pre-Merge
* [2021-08-26 09:08AM] Scrape Tentative Vax Schedule
  * Updated README
  * Pipeline done
  * new folders
  * Pipeline done
  * Done
  * Pre-Merge
  * Added gig
  * Updated lk-vax-schedule workflows
  * Fixed filename bug
  * Fixed filename bug
  * Fix vax-schedule folder bug
* [2021-08-26 10:27AM] Remove active/recovered from stats
  * Updated README
  * Removed active from SA update
  * Updated workflows
  * Updated LK Vax Update workflows
  * 
  * Pre-Merge
  * 
  * Fixed scrape_google_id bug
  * Uncomment non-Sputnik
* [2021-08-29 07:49PM] Analyze Vaccine Gaps
  * Updated README
  * Done
  * Done
  * Pre-Merge
* [2021-08-30 05:10PM] Analyze Vaccine Gaps 2
  * Updated README
  * Done
  * Pre-Merge
<<<<<<< HEAD
  * Updated README
=======
* [2021-08-31 03:54PM] Fix districts bug
  * Updated README
  * Pre-Merge
>>>>>>> fix-districts-bug
  * Reverted
  * Added Hambantota to get_correct_district
  * Reverted
  * Shell for analysis/mortality_curve.py
* [2021-09-01 01:32PM] Analyze Mortality Curve
  * Updated README
  * Pre-Merge
  * Fixed 20210907 PDF Name bug
  * Fixed 20210908_1 bug
  * Fixed 20210908_1 bug
  * Updated upload
  *  (2021-09-19-0650) Extended URL_LOAD_TIME = 20
  *  (2021-09-19-0717) Fixed scrape_pdf bug
  *  (2021-09-19-0720) Fixed various lint errors
  *  (2021-09-19-0721) Headless
  *  [2021-09-23 08:10PM] Delay LK Vax - Upload Data - Cron
  *  [2021-09-23 08:21PM] Fixed 20210922 Bug
  *  [2021-09-24 05:43PM] Fixed 20210923 bug
  *  [2021-09-26 07:11PM] Changed tweepy version
  *  [2021-11-15 08:57AM] Removed Cron Workflows
  *  [2021-12-22 08:59AM] More bugs
  *  [2021-12-22 09:39AM] Basic Tweet done
