# APA TODO

## Adding projects

Always looking for more awesome, so if you think you've found one we
missed, just file an issue and use the template! See CONTRIBUTING.md
for details.

See [the Candidates section](#Candidates) of this document for a queue of applications in
need of review. Ideally each of these would be moved to either the
primary list, the archive, or the revisit lists.

## Adding other information and structure

### Backfill URLs

Used to be we didn't collect as many links as we do now. For instance,
many projects have documentation, but we don't have a link to them.

Links we probably missed and should backfill:

* PyPI
* Wikipedia
* Funding

Some of this might be doable (semi-)automatically, using Apatite.

### Apatite

These documents are generated and managed with a purpose-built CLI
tool, [apatite](https://github.com/mahmoud/apatite). Apatite has [its
own TODO](https://github.com/mahmoud/apatite/blob/master/TODO.md),
which at the time of writing includes fun programmatic tasks like
autochecking links. The list has nearly a thousand links at the time
of writing, and we don't want to turn into a link graveyard like some
lists/wiki pages of yore.

### Taxonomy

Right now some topics are bursting at the seams with projects, and
there are still many projects in "misc" categories. More structure
would help keep the list navigable.

## Maintenance

* Right now integration is manual, so CI would be great.
  1. Validate PRs.
  2. Push back rendered changes straight from CI so users don't need
     apatite installed.
  3. Automate maintenance of the dataset used to in the included
     analysis notebook. (this is a doozy, will probably involve
     creating a huge, pre-warmed up container with 37GB+ repos for it
     to execute in reasonable time)

## Long-term vision

There are a lot of directions to take this data and related findings.

### Wikidata

I would like to see this list used to populate a list of notable
Python software projects to
[Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page). Someone
has to do the curation here, why not us?

Another direction would be to have a static site with search, filters,
and more. The goal here being that users will be able to more quickly
find applications which look like their own, and contain answers to
questions that are hard to search otherwise (e.g., what does a
dockerfile look like for full-fledged applications, what are secret
management solutions that scale down to small projects, etc.)

## Discovery

Finding applications can be tricky, as sites like GitHub and PyPI are
more geared toward libraries, and app stores tend not to differentiate
between open/closed source and Python/non-Python projects.

So, it can be a fun treasure hunt of poring over application
lists. There's one such list below, as well as other resources that
still need mining to keep the candidate list below growing.

### Pages to trawl

* https://bestpractices.coreinfrastructure.org/en/projects?gteq=100&sort=achieved_passing_at&sort_direction=desc
* https://www.reddit.com/r/pyxel/ / https://github.com/kitao/pyxel/network/dependents?package_id=UGFja2FnZS02MzQ5MTY1MQ%3D%3D
* https://github.com/PySimpleGUI/PySimpleGUI/network/dependents?package_id=UGFja2FnZS05MjkyNDU5MA%3D%3D
* https://github.com/pygame/pygame/network/dependents?package_id=UGFja2FnZS01MjQ3MDAxOQ%3D%3D
* https://www.pygame.org  # really wish there was an API here, or some sort of curation
* https://games.renpy.org/year/2019  # i dunnnnoooo

### Pages trawled

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

### Other lists

This is hardly the first attempt to curate a list of Python
software. Here are some other lists we've covered, and how they
compare to the APA.

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


### Current Candidates

* https://github.com/GNOME/postr
* https://github.com/vitorfs/bootcamp  # looks a bit unmaintained
* https://salsa.debian.org/debian-keyring/keyring
* https://github.com/qwj/python-proxy
* https://github.com/airspeed-velocity/asv
* https://github.com/EmpireProject/Empire (maybe, has a lot of powershell)
* https://github.com/lbryio/lbry-sdk
* https://github.com/golemfactory/golem
* https://github.com/zenhack/simp_le
* https://github.com/thombashi/sqlitebiter
* https://github.com/Codaone/DEXBot
* https://github.com/NuID/nebulousAD
* https://github.com/dipu-bd/lightnovel-crawler
* https://github.com/raiden-network/raiden  # blockchain, maybe too cynical
* https://github.com/JaDogg/pydoro
* https://github.com/ActivityWatch/aw-server
* https://github.com/ActivityWatch/activitywatch
* https://github.com/marcelstoer/nodemcu-pyflasher
* https://github.com/defaultnamehere/cookie_crimes
* https://github.com/DedSecInside/TorBot
* https://github.com/Drakkar-Software/OctoBot
* https://github.com/datawire/kubernaut
* https://github.com/frostming/legit
* https://github.com/pazz/alot
* https://github.com/languitar/autosuspend
* https://github.com/Blosc/bloscpack
* https://github.com/xfce-mirror/catfish
* https://github.com/cea-hpc/clustershell
* https://github.com/pixelb/crudini
* https://code.launchpad.net/dkimpy-milter
* https://github.com/otsaloma/gaupol
* https://github.com/regebro/hovercraft
* https://github.com/pimutils/khal
* https://github.com/insanum/gcalcli
* https://github.com/kupferlauncher/kupfer  # maybe, seems a bit quiet
* https://code.launchpad.net/menulibre  # maybe, it's updated, but hard to establish quality/popularity
* https://github.com/eonpatapon/mpDris2  # pretty niche
* https://github.com/bluesabre/mugshot  # also pretty niche
* https://github.com/jeromerobert/pdfarranger
* https://gitlab.com/pdftools/pdfposter
* https://github.com/sopel-irc/sopel
* https://github.com/PyCQA/prospector
* https://github.com/scheibler/khard
* https://github.com/pytrainer/pytrainer  # like a mini strava
* https://github.com/amanusk/s-tui
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
* https://github.com/scour-project/scour
* https://github.com/iovisor/bcc  # half python half c++
* https://github.com/stoq/stoq  # maybe discontinued? github is updated, but home page is empty
* https://github.com/netdata/netdata  # might belong better on a list of applications successfully using python for plugins
* https://github.com/microcosm-cc/microweb
* https://github.com/zopefoundation/ZEO
* https://github.com/manns/pyspread/
* https://github.com/oaubert/advene
* https://github.com/intoli/exodus
* https://github.com/burningmantech/ranger-ims-server
* https://github.com/psincraian/pepy
* https://github.com/crflynn/pypistats.org
* https://github.com/bram85/topydo
* https://github.com/nexedi/neoppod
* https://github.com/Kozea/wdb
* https://github.com/Scifabric/pybossa
* https://github.com/Flexget/Flexget
* https://github.com/RocketMap/RocketMap
* https://github.com/nerdvegas/rez
