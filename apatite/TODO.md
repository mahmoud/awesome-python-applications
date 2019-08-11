
# Fetching/pulling

* Fix outstanding git/hg/bzr clones, either with manual clone_urls or some other method (high pri)
  * solfege
  * sage
  * saleor
  * rhodecode
  * viewvc
  * gedit
* Add SVN support (low pri)

# Stats Ideas

* Hybridization / Co-occurrence with other languages (sloccount) (javascript, C, Cython, Java, etc.)
* Stars/forks (gh api, requires key) (also important for illustrating the contrast of scales in stars and collaboration)
* License (https://github.com/src-d/go-license-detector/releases)
* Packaging (containers: docker, snap, flatpak; freezers; setup.py/pypi, etc.)
* sloccount
* age / # of contributions, contributors. # of overlapping contributors.
* source control (git vs hg vs lp)

# Data collection

* command to delete/archive results older than a certain date?
* load all results files
* apatite collect --targets --metrics
* apatite collate --date
* apatite analyze collated_file.json
* apatite-results__2019-08-10T10-10-10__2019-08-10T10-10-10.json (oldest date__newest_date)
* look at all targets for the collection, take the oldest and newest
  dates, then generate results filename, then start data collection
* collection needs to take into account existing valid results and resume
* for results collation, accept a date, load all results files with
  that date within their range, keep newest results up to that date
* apatite tarchive, apatite merge-tarchive ? (for cross-host results
  merging if repeating collection takes too long)

## Collation

* Open all files with data between date ranges
* Scan through for unique combinations of supported metrics and still-listed projects
* Keep the most recent data (that isn't newer than the specified date)
  * isodates don't need to be parsed to be compared; stick to string comps for speed
* Future: Make note of which data is missing
