# TODO

* Issue templates
* Add tags to projects
  * License
  * py2/py3/py23
  * Frameworks
  * Target platform
  * Funding model? corporate, nonprofit, and donationware
* What to do with closed-source (dropbox, instagram, etc.)
* CI to check YAML, etc.
* CI to push back generated docs
* Automatic link checking (no duplicates, all resolving)
* Sort keys

## What is an application?

While generally it's pretty easy to tell the difference between a
library and an application, that doesn't mean there aren't tricky
cases. Here are some helpful questions to help classify Python software:

* Does the software favor non-code configuration (environment
  variables, ini/yaml/toml/json files, CLI args, etc.) versus writing
  more Python code? Software may seem like an application at first,
  but if it requires writing too much code, it may actually be a
  framework.
* Does the software feature a plugin system? Extending the previous
  point, applications won't require writing code, but well-developed
  ones may feature a structured way to extend them.
* Is the software installed using the pip package manager? Being
  installed with (or requiring) system package managers and installers
  is generally a pretty good sign you're looking at an application.


## Candidates

* https://github.com/belangeo/soundgrain
* https://github.com/albertz/music-player
* https://github.com/j3ffhubb/musikernel
* https://github.com/danboid/shufti
* https://github.com/examachine/pisi
* https://github.com/jedie/PyLucid  # distribution of django-cms?
* https://github.com/frePPLe/frepple  # more erp!
* https://github.com/rabbitvcs/rabbitvcs
* https://github.com/MeanEYE/Sunflower/
* https://github.com/gammu/wammu  # maybe
* https://github.com/thinkle/gourmet
* https://github.com/GNOME/postr
* https://launchpad.net/kabikaboo  # been a while since last release
* https://github.com/ozmartian/vidcutter
* https://github.com/senaite/senaite.lims / https://github.com/bikalims/bika.lims
* https://github.com/LinOTP/LinOTP
* https://github.com/sshuttle/sshuttle
* https://github.com/Maratyszcza/PeachPy (cli assembler, used by go, etc., https://blog.gopheracademy.com/advent-2016/peachpy/ https://github.com/digitalbrain79/NNPACK-darknet/blob/master/configure.py )

## AlternativeTo Trawl

https://alternativeto.net/software/cutecoin/ - need more review
https://alternativeto.net/software/pince/ - added
https://alternativeto.net/software/dontpanic/ - discontinued/offline
https://alternativeto.net/software/outspline/ - bit too small
https://alternativeto.net/software/dbpedia/ - mostly not python, lots of disparate components
https://alternativeto.net/software/meshroom/ -
https://alternativeto.net/software/magic-wormhole/
https://alternativeto.net/software/bms/
https://alternativeto.net/software/fame-automates-malware-evaluation/
https://alternativeto.net/software/space-shooter/
https://alternativeto.net/software/jam-py-postfix-aliases/
https://alternativeto.net/software/term2048/
https://alternativeto.net/software/scour/
https://alternativeto.net/software/shreddit/
https://alternativeto.net/software/bcc/
https://alternativeto.net/software/stoq/
https://alternativeto.net/software/activitywatch/
https://alternativeto.net/software/launchpad/
https://alternativeto.net/software/netdata/

## Pages scoured

Hardly the only sources, but mostly so others don't spend their time
mining a spent resource.

* https://wiki.python.org/moin/PyQt/SomeExistingApplications
* https://wiki.python.org/moin/PythonInMusic
* https://wiki.python.org/moin/Applications
* https://wiki.python.org/moin/WellKnownPythonPrograms
* https://en.wikipedia.org/wiki/List_of_Python_software#Applications
* https://en.wikipedia.org/wiki/PyGTK#Notable_applications_that_use_PyGTK
* http://pythonsource.com/
* http://openhub.net/ (python + pyqt4/5 + pygtk tags, pretty noisy dataset)

## Problems with other lists

This is hardly the first attempt to curate a list of Python
software. There are some differences this time around:

1. Objective criteria for inclusion
2. Guaranteed qualititative review (peer review, etc.)
3. Only applications, no frameworks or libraries
4. Links, specifically repo link required, for automated quality control (dead links, dead projects)
5. Structured, for automated consumption and reuse
6. Human-readable docs generated off of structured data
7. Open-source: contribute via PR
8. Tagged, tag aspects (tagsonomy)
9. Destination: Wikidata

Other superceded approaches:

* Wikipedia (https://en.wikipedia.org/wiki/List_of_Python_software)
   * No clear curation
   * Unstructured
* Wikidata
   * Lack of browsability
   * Incomplete dataset
   * Hard to curate
* wiki.python.org
   * Too many dead links and projects to count
   * Unstructured
   * Infrequent curation
   * Overinclusivity, minimal criteria
   * Unclear focus of "written in Python" and "supports Python" (in the case of IDEs/plugins)
   * Blurry on open-source and applications
* Awesome Python (https://github.com/vinta/awesome-python)
   * 98% libraries and frameworks for developer consumption, not exemplar applications
* http://pythonsource.com/
   * Good, but mingles applications with libraries/frameworks/engines
   * Unclear curatorship
   * No API
* Softpedia
   * All of the above (esp mingling libraries and applications)
* AlternativeTo
   * Pretty nice site focused on applications, but still suffers from
     most of the above, esp the lack of an API.
