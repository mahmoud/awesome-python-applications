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
* https://github.com/push-things/django-th  # good concept, but dev has slowed, looks kind of immature
* https://github.com/taroved/pol  # always a good concept, unsure about the adoption rate, code is a little bit disorganized
* https://kibitzr.github.io/
* https://github.com/vitorfs/bootcamp  # looks a bit unmaintained
* https://github.com/byro/byro
* https://salsa.debian.org/ftp-team/dak
* https://salsa.debian.org/qa/distro-tracker
* https://salsa.debian.org/debian-keyring/keyring
* https://github.com/spl0k/supysonic
* https://github.com/qwj/python-proxy
* https://github.com/airspeed-velocity/asv
* https://github.com/artisan-roaster-scope/artisan
* https://github.com/guardicore/monkey
* https://github.com/remyroy/CDDA-Game-Launcher
* https://github.com/EmpireProject/Empire (maybe, has a lot of powershell)
* https://github.com/lbryio/lbry-sdk
* https://github.com/golemfactory/golem
* https://github.com/cs01/gdbgui
* https://github.com/pyfa-org/Pyfa
* https://github.com/hubblestack/hubble
* https://github.com/jendrikseipp/rednotebook
* https://github.com/mstuttgart/pynocchio
* https://github.com/google/grr
* https://github.com/zenhack/simp_le
* https://github.com/thombashi/sqlitebiter
* https://github.com/malwaredllc/byob
* https://github.com/ctxis/CAPE
* https://github.com/Codaone/DEXBot
* https://github.com/usnistgov/mosaic
* https://github.com/NuID/nebulousAD
* https://github.com/chanzuckerberg/cellxgene
* https://github.com/dipu-bd/lightnovel-crawler
* https://github.com/delmic/odemis
* https://github.com/raiden-network/raiden  # blockchain, maybe too cynical
* https://github.com/JaDogg/pydoro
* https://github.com/arsenetar/dupeguru
* https://github.com/gridsync/gridsync
* https://github.com/ActivityWatch/aw-server
* https://github.com/overhangio/tutor
* https://github.com/borgbase/vorta
* https://github.com/marcelstoer/nodemcu-pyflasher
* https://github.com/defaultnamehere/cookie_crimes
* https://github.com/DedSecInside/TorBot
* https://github.com/Drakkar-Software/OctoBot
* https://github.com/datawire/kubernaut
* https://github.com/snapcore/snapcraft
* https://github.com/frostming/legit
* https://github.com/pazz/alot
* https://github.com/languitar/autosuspend
* https://github.com/Backblaze/B2_Command_Line_Tool  # backblaze, has bash completion
* https://github.com/Blosc/bloscpack
* https://github.com/xfce-mirror/catfish
* https://github.com/giuspen/cherrytree
* https://github.com/cea-hpc/clustershell
* https://github.com/pixelb/crudini
* https://github.com/cython/cython
* https://code.launchpad.net/dkimpy-milter
* https://github.com/otsaloma/gaupol
* https://github.com/sdg-mit/gitless
* https://github.com/regebro/hovercraft
* https://github.com/pimutils/khal
* https://github.com/insanum/gcalcli
* https://github.com/kupferlauncher/kupfer  # maybe, seems a bit quiet
* https://code.launchpad.net/menulibre  # maybe, it's updated, but hard to establish quality/popularity
* https://github.com/eonpatapon/mpDris2  # pretty niche
* https://github.com/bluesabre/mugshot  # also pretty niche
* https://github.com/HenriWahl/Nagstamon / https://nagstamon.ifw-dresden.de/
* https://github.com/otsaloma/nfoview
* https://github.com/jeromerobert/pdfarranger
* https://gitlab.com/pdftools/pdfposter
* https://github.com/sopel-irc/sopel
* https://github.com/platformio/platformio-core
* https://github.com/PyCQA/prospector
* https://github.com/scheibler/khard
* https://github.com/pytrainer/pytrainer  # like a mini strava
* https://github.com/rabbitvcs/rabbitvcs
* https://github.com/retext-project/retext
* https://github.com/amanusk/s-tui
* https://github.com/s3ql/s3ql  # i wonder what other fuse filesystems are implemented in python
* https://github.com/TomasTomecek/sen/
* https://github.com/SlapOS/slapos
* https://github.com/subdownloader/subdownloader
* https://github.com/ihabunek/toot/
* https://github.com/nschloe/tuna
* https://github.com/pimutils/vdirsyncer  # even with its questionable maintainer status
* https://github.com/DonyorM/weresync  # not sure it's actually as accessible as it claims to be
* https://github.com/jrfonseca/xdot.py
* https://github.com/ARMmbed/yotta
* https://github.com/newtdb/db
* https://git.duniter.org/clients/python/sakia / https://github.com/duniter/sakia
* https://github.com/certsocietegenerale/fame
* https://github.com/masfaraud/BMSpy
* https://github.com/tasdikrahman/spaceShooter # bit out of date, but it's a pygame game with a bit of fame
* https://github.com/bfontaine/term2048  # terminal game yay
* https://github.com/scour-project/scour
* https://github.com/iovisor/bcc  # half python half c++
* https://github.com/stoq/stoq  # maybe discontinued? github is updated, but home page is empty
* https://github.com/ActivityWatch/activitywatch
* https://launchpad.net/launchpad  # thought i added this
* https://github.com/netdata/netdata  # might belong better on a list of applications successfully using python for plugins

## Pages to trawl

* https://bestpractices.coreinfrastructure.org/en/projects?gteq=100&sort=achieved_passing_at&sort_direction=desc
* https://www.reddit.com/r/pyxel/ / https://github.com/kitao/pyxel/network/dependents?package_id=UGFja2FnZS02MzQ5MTY1MQ%3D%3D
* https://github.com/PySimpleGUI/PySimpleGUI/network/dependents?package_id=UGFja2FnZS05MjkyNDU5MA%3D%3D
* https://github.com/pygame/pygame/network/dependents?package_id=UGFja2FnZS01MjQ3MDAxOQ%3D%3D
* https://www.pygame.org  # really wish there was an API here, or some sort of curation
* https://games.renpy.org/year/2019  # i dunnnnoooo

## Pages trawled

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
* https://github.com/pyinstaller/pyinstaller/network/dependents
* https://alternativeto.net/ (python tag)
* https://git.duniter.org/explore/projects/

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
